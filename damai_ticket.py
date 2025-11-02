#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
大麦网抢票模块
"""

import os
import time
import json
import random
import logging
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service # 导入 Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger("DamaiTicket")

class DamaiTicket:
    def __init__(self, config):
        """初始化大麦网抢票类
        
        Args:
            config: 配置信息，包含登录信息、目标演出信息等
        """
        self.config = config
        self.session = requests.Session()
        self.driver = None
        self.is_login = False
        
        # 初始化浏览器
        self._init_browser()
        
    def _init_browser(self):
        """初始化浏览器"""
        options = webdriver.ChromeOptions()
        
        # 添加一些选项来优化抢票
        if not self.config.get('show_browser', False):
            options.add_argument('--headless')  # 无头模式
        
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # 设置用户代理
        options.add_argument(f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # 加载cookies
        if self.config.get('cookie_path') and os.path.exists(self.config['cookie_path']):
            options.add_argument(f'--user-data-dir={self.config["cookie_path"]}')
        
        # 指定 ChromeDriver 路径
        chromedriver_path = os.path.join(os.getcwd(), "chromedriver.exe")
        service = Service(executable_path=chromedriver_path) # 使用 Service 对象
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)
        
    def login(self):
        """登录大麦网"""
        if self.is_login:
            return True
            
        logger.info("开始登录大麦网...")
        
        # 打开登录页
        self.driver.get("https://passport.damai.cn/login")
        
        # 等待用户手动登录
        if self.config.get('manual_login', True):
            logger.info("请在浏览器中手动完成登录操作...")
            try:
                # 等待登录成功，通常登录成功后会跳转到用户中心或首页
                WebDriverWait(self.driver, 300).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "user-header"))
                )
                self.is_login = True
                logger.info("登录成功!")
                
                # 保存cookies
                if self.config.get('save_cookies', True):
                    cookies = self.driver.get_cookies()
                    with open('damai_cookies.json', 'w') as f:
                        json.dump(cookies, f)
                    logger.info("Cookies已保存")
                
                return True
            except TimeoutException:
                logger.error("登录超时，请重试")
                return False
        else:
            # 自动登录逻辑，需要用户名密码
            try:
                # 切换到账号密码登录
                switch_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "account-login"))
                )
                switch_btn.click()
                
                # 输入用户名密码
                username_input = self.driver.find_element(By.ID, "fm-login-id")
                password_input = self.driver.find_element(By.ID, "fm-login-password")
                
                username_input.send_keys(self.config['username'])
                password_input.send_keys(self.config['password'])
                
                # 点击登录按钮
                login_btn = self.driver.find_element(By.CLASS_NAME, "fm-btn")
                login_btn.click()
                
                # 等待登录成功
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "user-header"))
                )
                
                self.is_login = True
                logger.info("登录成功!")
                return True
            except Exception as e:
                logger.error(f"自动登录失败: {e}")
                return False
    
    def enter_concert(self):
        """进入演唱会页面"""
        logger.info(f"正在打开演出页面: {self.config['target_url']}")
        self.driver.get(self.config['target_url'])
        
        # 等待页面加载完成
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "perform__order__price"))
            )
            logger.info("演出页面加载成功")
            return True
        except TimeoutException:
            logger.error("演出页面加载超时")
            return False
    
    def choose_ticket(self):
        """选择票档"""
        try:
            # 等待票档元素加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "sku-item-container"))
            )
            
            # 获取所有票档
            ticket_elements = self.driver.find_elements(By.CLASS_NAME, "sku-item-container")
            
            # 根据配置选择票档
            target_ticket = self.config.get('ticket_type', '').strip()
            
            if target_ticket:
                # 查找指定票档
                for element in ticket_elements:
                    ticket_name = element.text
                    if target_ticket in ticket_name and "已售罄" not in ticket_name:
                        logger.info(f"选择票档: {ticket_name}")
                        element.click()
                        return True
                
                # 如果指定票档不可用，根据配置决定是否选择其他票档
                if self.config.get('allow_other_ticket', True):
                    for element in ticket_elements:
                        if "已售罄" not in element.text:
                            logger.info(f"指定票档不可用，选择: {element.text}")
                            element.click()
                            return True
                
                logger.warning("没有找到可用票档")
                return False
            else:
                # 没有指定票档，选择第一个可用的
                for element in ticket_elements:
                    if "已售罄" not in element.text:
                        logger.info(f"选择票档: {element.text}")
                        element.click()
                        return True
                
                logger.warning("没有找到可用票档")
                return False
                
        except Exception as e:
            logger.error(f"选择票档失败: {e}")
            return False
    
    def choose_count(self):
        """选择购票数量"""
        try:
            # 等待数量选择元素加载
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "cafe-c-input-number"))
            )
            
            # 获取数量加减按钮
            count_container = self.driver.find_element(By.CLASS_NAME, "cafe-c-input-number")
            add_btn = count_container.find_element(By.CLASS_NAME, "cafe-c-input-number-handler-up")
            
            # 设置购票数量
            ticket_count = min(int(self.config.get('ticket_count', 1)), 6)  # 大麦限购6张
            
            # 点击增加按钮
            for _ in range(ticket_count - 1):  # 默认数量是1，所以减1
                add_btn.click()
                time.sleep(0.2)
            
            logger.info(f"已选择 {ticket_count} 张票")
            return True
        except Exception as e:
            logger.error(f"选择购票数量失败: {e}")
            return False
    
    def submit_order(self):
        """提交订单"""
        try:
            # 点击立即购买按钮
            buy_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "buy-btn"))
            )
            buy_btn.click()
            logger.info("已点击立即购买")
            
            # 等待确认订单页面加载
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "submit-wrapper"))
            )
            
            # 勾选同意协议
            try:
                agree_checkbox = self.driver.find_element(By.CLASS_NAME, "agree-policy")
                if not agree_checkbox.is_selected():
                    agree_checkbox.click()
            except:
                pass  # 有些页面可能没有协议勾选
            
            # 点击提交订单按钮
            submit_btn = self.driver.find_element(By.CLASS_NAME, "submit-btn")
            submit_btn.click()
            
            logger.info("已提交订单")
            
            # 等待支付页面加载
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.url_contains("pay.damai.cn")
                )
                logger.info("抢票成功，请在30分钟内完成支付!")
                return True
            except TimeoutException:
                logger.warning("等待支付页面超时，可能抢票失败")
                return False
            
        except Exception as e:
            logger.error(f"提交订单失败: {e}")
            return False
    
    def run(self):
        """运行抢票主流程"""
        try:
            # 登录
            if not self.login():
                logger.error("登录失败，退出程序")
                return False
            
            # 进入演唱会页面
            if not self.enter_concert():
                logger.error("进入演出页面失败，退出程序")
                return False
            
            # 如果有设置开售时间，则等待
            if self.config.get('sale_time'):
                self.wait_for_sale()
            
            # 开始抢票循环
            retry_times = int(self.config.get('retry_times', 10))
            for i in range(retry_times):
                logger.info(f"第 {i+1}/{retry_times} 次抢票尝试")
                
                # 刷新页面
                if i > 0:
                    self.driver.refresh()
                    time.sleep(1)
                
                # 选择票档
                if not self.choose_ticket():
                    continue
                
                # 选择数量
                if not self.choose_count():
                    continue
                
                # 提交订单
                if self.submit_order():
                    logger.info("抢票成功!")
                    return True
            
            logger.warning(f"尝试 {retry_times} 次后仍未抢到票")
            return False
            
        except Exception as e:
            logger.error(f"抢票过程发生异常: {e}")
            return False
        finally:
            # 保持浏览器打开一段时间，方便用户查看
            if self.config.get('keep_browser', True):
                time.sleep(60)
            else:
                self.driver.quit()
    
    def wait_for_sale(self):
        """等待开售"""
        sale_time_str = self.config['sale_time']
        sale_time = datetime.strptime(sale_time_str, "%Y-%m-%d %H:%M:%S")
        
        now = datetime.now()
        if now >= sale_time:
            logger.info("当前已过开售时间，直接开始抢票")
            return
        
        wait_seconds = (sale_time - now).total_seconds()
        logger.info(f"距离开售还有 {wait_seconds:.2f} 秒，等待中...")
        
        # 提前10秒开始准备
        if wait_seconds > 10:
            time.sleep(wait_seconds - 10)
            logger.info("准备抢票，倒计时10秒...")
            
        # 最后10秒内，每秒刷新一次页面
        remaining = min(10, wait_seconds)
        for i in range(int(remaining)):
            time.sleep(1)
            logger.info(f"倒计时: {int(remaining)-i} 秒")
            self.driver.refresh()
        
        # 确保时间精确，等到整点再开始
        while datetime.now() < sale_time:
            time.sleep(0.01)
        
        logger.info("开售时间到，开始抢票!")