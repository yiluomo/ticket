#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
抢票脚本主程序
支持大麦网和B站展会的抢票功能
"""

import os
import sys
import time
import json
import logging
import argparse
from datetime import datetime

from damai_ticket import DamaiTicket
from bilibili_ticket import BilibiliTicket

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ticket_sniper.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TicketSniper")

def load_config(config_file='config.json'):
    """加载配置文件"""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        sys.exit(1)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='抢票脚本 - 支持大麦网和B站展会')
    parser.add_argument('--platform', type=str, choices=['damai', 'bilibili', 'all'], 
                        default='all', help='选择抢票平台: damai(大麦), bilibili(B站), all(全部)')
    parser.add_argument('--config', type=str, default='config.json', 
                        help='配置文件路径')
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config)
    
    # 根据选择的平台启动抢票
    if args.platform in ['damai', 'all'] and 'damai' in config:
        logger.info("启动大麦网抢票...")
        damai = DamaiTicket(config['damai'])
        damai.run()
    
    if args.platform in ['bilibili', 'all'] and 'bilibili' in config:
        logger.info("启动B站展会抢票...")
        bilibili = BilibiliTicket(config['bilibili'])
        bilibili.run()
    
    logger.info("抢票任务已完成")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("用户中断程序")
    except Exception as e:
        logger.error(f"程序异常: {e}")