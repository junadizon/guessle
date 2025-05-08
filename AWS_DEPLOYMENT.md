# AWS EC2 Deployment Guide for Guessle Bot

## Table of Contents
- [1. Setting Up EC2 Instance](#1-setting-up-ec2-instance)
- [2. Connecting to EC2](#2-connecting-to-ec2)
- [3. Bot Deployment](#3-bot-deployment)
- [4. Monitoring and Maintenance](#4-monitoring-and-maintenance)
- [5. Security Best Practices](#5-security-best-practices)
- [6. Cost Optimization](#6-cost-optimization)

## 1. Setting Up EC2 Instance

### 1.1 Launch Instance
1. Go to AWS Console → EC2
2. Click "Launch Instance"
3. Configure instance:
   - Name: `guessle-bot`
   - AMI: Amazon Linux 2023
   - Instance type: t2.micro (free tier)
   - Key pair: Create new (save .pem file)
   - Network settings:
     - Allow SSH (port 22)
     - Allow HTTP (port 8080)
   - Storage: 8GB (free tier)

### 1.2 Security Group Setup
Create security group `guessle-bot-sg` with rules:
- Inbound:
  - SSH (22): Your IP
  - HTTP (8080): 0.0.0.0/0
  - HTTPS (443): 0.0.0.0/0
- Outbound:
  - All traffic: 0.0.0.0/0

## 2. Connecting to EC2

### 2.1 Local Machine Setup
1. Save your .pem file securely
2. Set correct permissions:
```bash
chmod 400 guessle-bot.pem
```

### 2.2 SSH Connection
```bash
ssh -i guessle-bot.pem ec2-user@YOUR_INSTANCE_PUBLIC_IP
```

## 3. Bot Deployment

### 3.1 System Setup
```bash
# Update system
sudo yum update -y

# Install required packages
sudo yum install python3 python3-pip git -y
```

### 3.2 Bot Installation
```bash
# Create and enter directory
mkdir guessle-bot
cd guessle-bot

# Clone repository
git clone YOUR_REPOSITORY_URL .

# Install dependencies
pip3 install -r requirements.txt
```

### 3.3 Environment Configuration
1. Create .env file:
```bash
nano .env
```

2. Add required variables:
```
DISCORD_TOKEN=your_discord_token_here
DATABASE_URL=your_database_url_here
PORT=8080
```

3. Set permissions:
```bash
chmod 600 .env
```

### 3.4 Service Setup
1. Create service file:
```bash
sudo nano /etc/systemd/system/guessle-bot.service
```

2. Add service configuration:
```ini
[Unit]
Description=Guessle Discord Bot
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/guessle-bot
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

3. Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable guessle-bot
sudo systemctl start guessle-bot
```

## 4. Monitoring and Maintenance

### 4.1 Check Bot Status
```bash
# Check service status
sudo systemctl status guessle-bot

# View logs
sudo journalctl -u guessle-bot -f
```

### 4.2 Common Commands
```bash
# Restart bot
sudo systemctl restart guessle-bot

# Stop bot
sudo systemctl stop guessle-bot

# Start bot
sudo systemctl start guessle-bot
```

### 4.3 Troubleshooting
1. Check logs for errors:
```bash
sudo journalctl -u guessle-bot -n 50
```

2. Verify environment variables:
```bash
cat .env
```

3. Test web server:
```bash
curl http://localhost:8080/health
```

## 5. Security Best Practices
1. Keep .pem file secure
2. Regularly update system: `sudo yum update -y`
3. Monitor AWS CloudWatch for instance metrics
4. Set up AWS Budget alerts
5. Use IAM roles instead of hardcoded credentials

## 6. Cost Optimization
1. Use AWS Free Tier monitoring
2. Set up auto-shutdown during inactive periods
3. Monitor usage in AWS Billing Console
4. Set up AWS Budget alerts

## Common Issues and Solutions

### Bot Not Starting
1. Check environment variables:
```bash
cat .env
```

2. Check logs:
```bash
sudo journalctl -u guessle-bot -f
```

3. Verify Python installation:
```bash
python3 --version
```

### Connection Issues
1. Verify security group settings
2. Check instance status in AWS Console
3. Ensure .pem file permissions are correct
4. Verify your IP is allowed in security group

### Database Connection Issues
1. Verify DATABASE_URL in .env
2. Check database security settings
3. Ensure database is accessible from EC2

## Additional Resources
- [AWS EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Systemd Service Documentation](https://www.freedesktop.org/software/systemd/man/systemd.service.html)