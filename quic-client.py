import argparse
import asyncio
import json
import logging
import ssl
from time import sleep
from typing import Optional, cast

from aioquic.asyncio.client import connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent
from aioquic.quic.logger import QuicFileLogger

logger = logging.getLogger("client")


class EchoClient(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._ack_waiter: Optional[asyncio.Future[None]] = None

    async def send(self, datagram) -> None:
        self._quic.send_datagram_frame(datagram)
        waiter = self._loop.create_future()
        self._ack_waiter = waiter
        self.transmit()
        return await asyncio.shield(waiter)

    def quic_event_received(self, event: QuicEvent) -> None:
        if self._ack_waiter is not None:
            waiter = self._ack_waiter
            self._ack_waiter = None
            waiter.set_result(None)


async def run(configuration: QuicConfiguration, host: str, port: int) -> None:
    async with connect(
        host, port, configuration=configuration, create_protocol=EchoClient
    ) as client:
        client = cast(EchoClient, client)
        logger.info("sending msg")
        for i in range(100):
            logger.info(f"sequence: {str(i).zfill(4)}")
            await client.send(json.dumps({"position": {"x": i, "y": i, "z": i}}).encode())
            sleep(1/100)
        logger.info("received msg")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QUIC Echo client")
    
    parser.add_argument(
        "host", type=str, help="server host"
    )
    parser.add_argument("port", type=int, help="server port")

    parser.add_argument(
        "-k",
        "--insecure",
        action="store_true",
        help="if true, do not validate server",
    )
    parser.add_argument(
        "-q",
        "--quic-log",
        type=str,
        help="specify directory for QLOG files",
    )
    parser.add_argument(
        "-l",
        "--secrets-log",
        type=str,
        help="log secrets to a file, for use with Wireshark",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="increase logging verbosity"
    )

    args = parser.parse_args()

    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        level=logging.DEBUG if args.verbose else logging.INFO,
    )

    configuration = QuicConfiguration(
        alpn_protocols=["h3-32"], is_client=True, max_datagram_frame_size=65536
    )
    configuration.verify_mode = ssl.CERT_NONE
    if args.quic_log:
        configuration.quic_logger = QuicFileLogger(args.quic_log)
    if args.secrets_log:
        configuration.secrets_log_file = open(args.secrets_log, "a")

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        run(configuration=configuration, host=args.host, port=args.port)
    )