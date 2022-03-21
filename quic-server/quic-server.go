// simple echo

package quicserver

import (
	"context"
	"crypto/rand"
	"crypto/rsa"
	"crypto/tls"
	"crypto/x509"
	"encoding/pem"
	"fmt"
	"log"
	"math/big"

	"github.com/lucas-clemente/quic-go"
)

func Run(addr string) {
	tlsConfig := &tls.Config{
		Certificates: []tls.Certificate{tlsCert()},
		NextProtos:   []string{"h3-32"},
	}

	quicConfig := &quic.Config{
		EnableDatagrams: true,
	}

	lis, err := quic.ListenAddr(addr, tlsConfig, quicConfig)

	if err != nil {
		panic(err)
	}

	for {
		sess, err := lis.Accept(context.TODO())
		if err != nil {
			panic(err)
		}

		go func() {
			fmt.Print("start quic-server")
			for {
				msg, err := sess.ReceiveMessage()
				if err != nil {
					log.Print(err)
					return
				}

				if err := sess.SendMessage(msg); err != nil {
					log.Print(err)
					return
				}
			}
		}()
	}
}

func tlsCert() tls.Certificate {
	key, _ := rsa.GenerateKey(rand.Reader, 2048)
	template := x509.Certificate{SerialNumber: big.NewInt(1)}
	certDER, _ := x509.CreateCertificate(rand.Reader, &template, &template, &key.PublicKey, key)
	keyPEM := pem.EncodeToMemory(&pem.Block{Type: "RSA PRIVATE KEY", Bytes: x509.MarshalPKCS1PrivateKey(key)})
	certPEM := pem.EncodeToMemory(&pem.Block{Type: "CERTIFICATE", Bytes: certDER})
	tlsCert, _ := tls.X509KeyPair(certPEM, keyPEM)
	return tlsCert
}
