# Smart Locker System - Deployment Guide

## Overview

This guide covers deploying the Smart Locker System in various environments, from development to production. The system consists of a Flask backend API and a React frontend application.

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+ recommended), macOS, or Windows
- **Python**: 3.8 or higher
- **Node.js**: 16.0 or higher
- **Database**: PostgreSQL only

# Example DATABASE_URL for PostgreSQL

DATABASE_URL=postgresql://username:password@localhost:5432/smart_locker_db

- **Web Server**: Nginx (production) or built-in Flask server (development)
- **Memory**: Minimum 2GB RAM, 4GB+ recommended
- **Storage**: 10GB+ available space

### Software Dependencies

- Git
- Python pip
- Node.js npm
- Nginx (production)
- Supervisor or systemd (production)

## Development Deployment

### Quick Start (Recommended)

1. **Clone and setup**

   ```bash
   git clone <repository-url>
   cd smart_locker_project
   ```

2. **Use the startup script**

   ```bash
   # Start without demo data
   ./start_dev.sh

   # Start with demo data for testing
   ./start_dev.sh --demo
   ```

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5050

### Manual Development Setup

1. **Backend setup**

   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Initialize database
   python -c "from app import init_db; init_db()"

   # Start backend server
   python app.py --port 5050 --demo
   ```

2. **Frontend setup**

   ```bash
   # Install dependencies
   npm install

   # Start development server
   npm run dev
   ```

## Production Deployment

### Option 1: Docker Deployment (Recommended)

1. **Create Dockerfile**

   ```dockerfile
   # Backend Dockerfile
   FROM python:3.9-slim

   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt

   COPY . .
   EXPOSE 5050

   CMD ["gunicorn", "--bind", "0.0.0.0:5050", "--workers", "4", "app:app"]
   ```

2. **Create docker-compose.yml**

   ```yaml
   version: "3.8"
   services:
     backend:
       build: .
       ports:
         - "5050:5050"
       environment:
         - FLASK_ENV=production
         - JWT_SECRET_KEY=your-secret-key
       volumes:
         - ./db:/app/db

     frontend:
       build: ./frontend
       ports:
         - "80:80"
       depends_on:
         - backend
   ```

3. **Deploy with Docker**
   ```bash
   docker-compose up -d
   ```

### Option 2: Traditional Server Deployment

#### Step 1: Server Preparation

1. **Update system**

   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install dependencies**

   ```bash
   sudo apt install python3 python3-pip python3-venv nginx supervisor -y
   curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash -
   sudo apt install nodejs -y
   ```

3. **Create application user**
   ```bash
   sudo useradd -m -s /bin/bash smartlocker
   sudo usermod -aG sudo smartlocker
   ```

#### Step 2: Application Deployment

1. **Clone application**

   ```bash
   sudo -u smartlocker git clone <repository-url> /home/smartlocker/app
   cd /home/smartlocker/app
   ```

2. **Setup Python environment**

   ```bash
   sudo -u smartlocker python3 -m venv .venv
   sudo -u smartlocker .venv/bin/pip install -r requirements.txt
   ```

3. **Setup Node.js environment**

   ```bash
   sudo -u smartlocker npm install
   sudo -u smartlocker npm run build
   ```

4. **Initialize database**
   ```bash
   sudo -u smartlocker .venv/bin/python -c "from app import init_db; init_db()"
   ```

#### Step 3: Gunicorn Configuration

1. **Create Gunicorn configuration**

   ```bash
   sudo nano /etc/supervisor/conf.d/smartlocker.conf
   ```

   ```ini
   [program:smartlocker]
   directory=/home/smartlocker/app
   command=/home/smartlocker/app/.venv/bin/gunicorn --bind 127.0.0.1:5050 --workers 4 --timeout 120 app:app
   user=smartlocker
   autostart=true
   autorestart=true
   stderr_logfile=/var/log/smartlocker/err.log
   stdout_logfile=/var/log/smartlocker/out.log
   environment=FLASK_ENV="production",JWT_SECRET_KEY="your-secret-key"
   ```

2. **Create log directory**

   ```bash
   sudo mkdir -p /var/log/smartlocker
   sudo chown smartlocker:smartlocker /var/log/smartlocker
   ```

3. **Start supervisor**
   ```bash
   sudo supervisorctl reread
   sudo supervisorctl update
   sudo supervisorctl start smartlocker
   ```

#### Step 4: Nginx Configuration

1. **Create Nginx configuration**

   ```bash
   sudo nano /etc/nginx/sites-available/smartlocker
   ```

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       # Frontend static files
       location / {
           root /home/smartlocker/app/dist;
           try_files $uri $uri/ /index.html;
       }

       # Backend API
       location /api {
           proxy_pass http://127.0.0.1:5050;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }

       # Security headers
       add_header X-Frame-Options "SAMEORIGIN" always;
       add_header X-XSS-Protection "1; mode=block" always;
       add_header X-Content-Type-Options "nosniff" always;
       add_header Referrer-Policy "no-referrer-when-downgrade" always;
       add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
   }
   ```

2. **Enable site**
   ```bash
   sudo ln -s /etc/nginx/sites-available/smartlocker /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

#### Step 5: SSL Configuration (Optional but Recommended)

1. **Install Certbot**

   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   ```

2. **Obtain SSL certificate**

   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

3. **Auto-renewal**
   ```bash
   sudo crontab -e
   # Add: 0 12 * * * /usr/bin/certbot renew --quiet
   ```

## Environment Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-super-secret-key-change-this
JWT_SECRET_KEY=your-jwt-secret-key-change-this

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/smart_locker_db
# For PostgreSQL: postgresql://user:password@localhost/smartlocker
# For MySQL: mysql://user:password@localhost/smartlocker

# Application Configuration
APP_PORT=5050
APP_HOST=0.0.0.0

# Security Configuration
CORS_ORIGINS=http://localhost:5173,https://your-domain.com
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/var/log/smartlocker/app.log

# Export Configuration
EXPORT_DIR=/var/exports/smartlocker
```

### Production Security Checklist

- [ ] Change default secret keys
- [ ] Use HTTPS in production
- [ ] Configure proper CORS origins
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Configure secure session settings
- [ ] Set up monitoring and logging
- [ ] Regular security updates
- [ ] Database backup strategy
- [ ] SSL certificate management

## Monitoring and Logging

### Application Logging

1. **Configure logging in app.py**

   ```python
   import logging
   from logging.handlers import RotatingFileHandler

   if not app.debug:
       file_handler = RotatingFileHandler('logs/smartlocker.log', maxBytes=10240, backupCount=10)
       file_handler.setFormatter(logging.Formatter(
           '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
       ))
       file_handler.setLevel(logging.INFO)
       app.logger.addHandler(file_handler)
       app.logger.setLevel(logging.INFO)
       app.logger.info('Smart Locker startup')
   ```

2. **System monitoring with systemd**
   ```bash
   sudo systemctl status smartlocker
   sudo journalctl -u smartlocker -f
   ```

### Performance Monitoring

1. **Install monitoring tools**

   ```bash
   sudo apt install htop iotop nethogs -y
   ```

2. **Database monitoring**

   ```bash
   # For SQLite
   sqlite3 db/locker.db "PRAGMA integrity_check;"

   # For PostgreSQL
   sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
   ```

## Backup and Recovery

### Database Backup

1. **SQLite backup script**

   ```bash
   #!/bin/bash
   BACKUP_DIR="/var/backups/smartlocker"
   DATE=$(date +%Y%m%d_%H%M%S)

   mkdir -p $BACKUP_DIR
   cp /home/smartlocker/app/db/locker.db $BACKUP_DIR/locker_$DATE.db

   # Keep only last 7 days of backups
   find $BACKUP_DIR -name "locker_*.db" -mtime +7 -delete
   ```

2. **Automated backup with cron**
   ```bash
   sudo crontab -e
   # Add: 0 2 * * * /home/smartlocker/backup.sh
   ```

### Application Backup

1. **Full application backup**

   ```bash
   #!/bin/bash
   BACKUP_DIR="/var/backups/smartlocker"
   DATE=$(date +%Y%m%d_%H%M%S)

   tar -czf $BACKUP_DIR/app_$DATE.tar.gz /home/smartlocker/app
   ```

## Troubleshooting

### Common Issues

1. **Port already in use**

   ```bash
   sudo netstat -tulpn | grep :5050
   sudo kill -9 <PID>
   ```

2. **Permission denied**

   ```bash
   sudo chown -R smartlocker:smartlocker /home/smartlocker/app
   sudo chmod -R 755 /home/smartlocker/app
   ```

3. **Database locked**

   ```bash
   sudo systemctl restart smartlocker
   ```

4. **Nginx configuration error**
   ```bash
   sudo nginx -t
   sudo systemctl restart nginx
   ```

### Debug Mode

For troubleshooting, enable debug mode temporarily:

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py --port 5050
```

## Scaling Considerations

### Horizontal Scaling

1. **Load balancer setup**

   ```nginx
   upstream smartlocker_backend {
       server 127.0.0.1:5050;
       server 127.0.0.1:5051;
       server 127.0.0.1:5052;
   }
   ```

2. **Database scaling**
   - Consider PostgreSQL for larger deployments
   - Implement database connection pooling
   - Set up read replicas for heavy read workloads

### Performance Optimization

1. **Caching**

   - Implement Redis for session storage
   - Add response caching for static data
   - Use CDN for static assets

2. **Database optimization**
   - Add appropriate indexes
   - Optimize queries
   - Implement connection pooling

## Maintenance

### Regular Maintenance Tasks

1. **Weekly**

   - Check log files for errors
   - Monitor disk space usage
   - Review security updates

2. **Monthly**

   - Update dependencies
   - Review performance metrics
   - Test backup and recovery procedures

3. **Quarterly**
   - Security audit
   - Performance review
   - Update SSL certificates

### Update Procedures

1. **Application updates**

   ```bash
   cd /home/smartlocker/app
   sudo -u smartlocker git pull
   sudo -u smartlocker .venv/bin/pip install -r requirements.txt
   sudo -u smartlocker npm install
   sudo -u smartlocker npm run build
   sudo supervisorctl restart smartlocker
   ```

2. **System updates**
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo systemctl restart nginx
   ```

## Support and Resources

### Documentation

- [Flask Deployment Guide](https://flask.palletsprojects.com/en/2.0.x/deploying/)
- [Nginx Configuration](https://nginx.org/en/docs/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)

### Monitoring Tools

- [Prometheus](https://prometheus.io/) - Metrics collection
- [Grafana](https://grafana.com/) - Visualization
- [Sentry](https://sentry.io/) - Error tracking

### Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security](https://flask-security.readthedocs.io/)
- [Nginx Security](https://nginx.org/en/docs/http/ngx_http_ssl_module.html)
