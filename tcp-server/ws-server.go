package tcpserver

import (
	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
	"golang.org/x/net/websocket"
)

func Run(addr string) error {
	e := echo.New()
	e.Use(middleware.Logger())
	e.Static("/", "public")

	e.GET("/", handleWebSocket)
	e.Logger.Fatal(e.Start(addr))

	return nil
}

func handleWebSocket(c echo.Context) error {
	websocket.Handler(func(ws *websocket.Conn) {
		defer ws.Close()

		for {
			msg := ""
			err := websocket.Message.Receive(ws, &msg)
			if err != nil {
				c.Logger().Error(err)
				return 
			}

			err = websocket.Message.Send(ws, msg)
			if err != nil {
				c.Logger().Error(err)
				return 
			}
		}
	}).ServeHTTP(c.Response(), c.Request())
	return nil
}