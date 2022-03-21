package main

import quicserver "github.com/sandship/ws-wt/quic-server"

func main() {

	// tcpserver.Run("0.0.0.0:18080")
	quicserver.Run("0.0.0.0:18081")

}