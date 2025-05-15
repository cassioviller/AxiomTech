import express, { type Request, Response, NextFunction } from "express";
import { registerRoutes } from "./routes";
import { setupVite, serveStatic, log } from "./vite";

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

app.use((req, res, next) => {
  const start = Date.now();
  const path = req.path;
  let capturedJsonResponse: Record<string, any> | undefined = undefined;

  const originalResJson = res.json;
  res.json = function (bodyJson, ...args) {
    capturedJsonResponse = bodyJson;
    return originalResJson.apply(res, [bodyJson, ...args]);
  };

  res.on("finish", () => {
    const duration = Date.now() - start;
    if (path.startsWith("/api")) {
      let logLine = `${req.method} ${path} ${res.statusCode} in ${duration}ms`;
      if (capturedJsonResponse) {
        logLine += ` :: ${JSON.stringify(capturedJsonResponse)}`;
      }

      if (logLine.length > 80) {
        logLine = logLine.slice(0, 79) + "…";
      }

      log(logLine);
    }
  });

  next();
});

(async () => {
  const server = await registerRoutes(app);

  app.use((err: any, _req: Request, res: Response, _next: NextFunction) => {
    const status = err.status || err.statusCode || 500;
    const message = err.message || "Internal Server Error";

    res.status(status).json({ message });
    throw err;
  });

  // importantly only setup vite in development and after
  // setting up all the other routes so the catch-all route
  // doesn't interfere with the other routes
  if (app.get("env") === "development") {
    await setupVite(app, server);
  } else {
    serveStatic(app);
  }

  // Configuração para produção (Docker/EasyPanel): Porta 6000
  // Configuração para desenvolvimento (Replit): Portas 5000 e 6000
  const prodPort = 6000;
  const devPort = 5000;

  // Em produção, escuta apenas na porta 6000
  if (app.get("env") === "production") {
    server.listen({
      port: prodPort,
      host: "0.0.0.0",
      reusePort: true,
    }, () => {
      log(`serving on port ${prodPort} (production)`);
    });
  } 
  // Em desenvolvimento, escuta em ambas as portas para compatibilidade
  else {
    // Criamos um segundo servidor para a porta 5000 (compatibilidade com Replit)
    import('http').then(({ createServer }) => {
      const devServer = createServer(app);
      
      // Inicia na porta 6000 (nossa porta padrão)
      server.listen({
        port: prodPort,
        host: "0.0.0.0",
        reusePort: true,
      }, () => {
        log(`serving on port ${prodPort} (development)`);
      });
      
      // Também inicia na porta 5000 (para workflow Replit)
      devServer.listen({
        port: devPort,
        host: "0.0.0.0",
        reusePort: true,
      }, () => {
        log(`serving on port ${devPort} (for Replit workflow)`);
      });
    });
  }
})();
