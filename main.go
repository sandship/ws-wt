package main

import tcpserver "github.com/sandship/ws-wt/tcp-server"

func main() {

	tcpserver.Run("0.0.0.0:18080")
	// quicserver.Run("0.0.0.0:18081")

}