import requests
import datetime
import time
import os
import webbrowser
import json
import sys
from urllib.parse import urlparse
from typing import Optional, Dict, Any

class APICrawler:
    """API爬虫工具类"""
    
    def __init__(self):
        self.visited_today = False
        self.last_save_dir = None
        self.success_count = 0
        self.fail_count = 0
        self.supported_formats = {
            'image': ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'],
            'video': ['mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv'],
            'audio': ['mp3', 'wav', 'flac', 'aac', 'm4a'],
            'text': ['txt', 'json', 'xml', 'html', 'csv']
        }
        
    def print_banner(self):
        """打印欢迎横幅"""
        print("=" * 60)
        print("🕷️  API爬虫工具 v2.1 - 效率优化版")
        print("=" * 60)
        print("✨ 支持多格式：图片、视频、音频、文本")
        print("🚀 智能识别：自动检测内容类型")
        print("📦 批量下载：支持连续作业")
        print("🛡️  安全合规：内置防封机制")
        print("⚡ 效率优化：智能目录管理 + 高速下载")
        print("=" * 60)

    def validate_url(self, url: str) -> bool:
        """验证URL格式"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def get_content_type(self, response: requests.Response) -> str:
        """智能识别内容类型"""
        content_type = response.headers.get('Content-Type', '').lower()
        
        # 根据Content-Type判断
        if 'text' in content_type or 'json' in content_type or 'xml' in content_type:
            return 'text'
        elif 'image' in content_type:
            return 'image'
        elif 'video' in content_type:
            return 'video'
        elif 'audio' in content_type:
            return 'audio'
        else:
            # 根据内容特征判断
            content = response.content
            if content.startswith(b'{') or content.startswith(b'['):
                return 'text'  # JSON
            elif content.startswith(b'\x89PNG') or content.startswith(b'\xff\xd8'):
                return 'image'
            elif content.startswith(b'\x00\x00\x00\x20ftyp'):
                return 'video'
            else:
                return 'binary'

    def generate_filename(self, content_type: str, media_type: str = None) -> str:
        """生成唯一文件名"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        
        if content_type == 'text':
            ext = media_type if media_type in self.supported_formats['text'] else 'txt'
            return f"data_{timestamp}.{ext}"
        elif content_type == 'image':
            ext = media_type if media_type in self.supported_formats['image'] else 'jpg'
            return f"image_{timestamp}.{ext}"
        elif content_type == 'video':
            ext = media_type if media_type in self.supported_formats['video'] else 'mp4'
            return f"video_{timestamp}.{ext}"
        elif content_type == 'audio':
            ext = media_type if media_type in self.supported_formats['audio'] else 'mp3'
            return f"audio_{timestamp}.{ext}"
        else:
            return f"file_{timestamp}.{media_type or 'bin'}"

    def save_content(self, response: requests.Response, save_dir: str, filename: str) -> bool:
        """保存内容到文件"""
        try:
            content_type = self.get_content_type(response)
            filepath = os.path.join(save_dir, filename)
            
            if content_type == 'text':
                # 保存文本内容
                content = response.text
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                # 保存二进制内容
                content = response.content
                with open(filepath, 'wb') as f:
                    f.write(content)
            
            return True
        except Exception as e:
            print(f"❌ 保存文件失败: {e}")
            return False

    def crawl_api(self, url: str, count: int, media_type: str, save_dir: str) -> Dict[str, Any]:
        """爬取API接口（效率优化版）"""
        
        # 优化请求头，提高成功率
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        results = {'success': 0, 'failed': 0, 'files': []}
        
        # 创建会话，提高性能
        session = requests.Session()
        session.headers.update(headers)
        
        print(f"🚀 开始爬取 {url}，共 {count} 个文件")
        print("=" * 50)
        
        # 批量处理优化
        batch_size = min(10, count)  # 每批处理10个或总数
        success_count = 0
        
        for i in range(count):
            try:
                print(f"📥 正在下载第 {i+1}/{count} 个文件...", end='', flush=True)
                
                # 使用会话发送请求，提高性能
                response = session.get(url, timeout=30, allow_redirects=True)
                
                if response.status_code == 200:
                    # 生成文件名
                    filename = self.generate_filename(self.get_content_type(response), media_type)
                    
                    # 保存文件
                    if self.save_content(response, save_dir, filename):
                        print(f" ✅ 成功 - {filename}")
                        results['success'] += 1
                        results['files'].append(filename)
                        success_count += 1
                    else:
                        print(f" ❌ 保存失败")
                        results['failed'] += 1
                else:
                    print(f" ❌ 请求失败 (状态码: {response.status_code})")
                    results['failed'] += 1
                
                # 智能延迟策略
                if success_count % batch_size == 0 and success_count > 0:
                    # 每成功处理一批后，稍微增加延迟
                    delay = min(2, 0.5 + (success_count // batch_size) * 0.1)
                    time.sleep(delay)
                elif response.status_code != 200:
                    # 请求失败时增加延迟
                    time.sleep(2)
                else:
                    # 正常请求使用较短延迟
                    time.sleep(0.3)
                
            except requests.exceptions.Timeout:
                print(f" ❌ 请求超时")
                results['failed'] += 1
                time.sleep(3)  # 超时后增加延迟
            except requests.exceptions.ConnectionError:
                print(f" ❌ 连接错误")
                results['failed'] += 1
                time.sleep(5)  # 连接错误后增加延迟
            except requests.exceptions.RequestException as e:
                print(f" ❌ 网络错误: {e}")
                results['failed'] += 1
                time.sleep(2)
            except Exception as e:
                print(f" ❌ 未知错误: {e}")
                results['failed'] += 1
                time.sleep(1)
        
        # 关闭会话
        session.close()
        return results

    def get_user_input(self):
        """获取用户输入（优化版）"""
        print("\n📝 请输入爬取参数：")
        
        # 获取API接口地址
        while True:
            url = input("请输入API接口地址: ").strip()
            if self.validate_url(url):
                break
            print("❌ 无效的URL格式，请重新输入！")
        
        # 获取爬取数量
        while True:
            try:
                count = int(input("请输入爬取数量 (1-1000): "))
                if 1 <= count <= 1000:
                    break
                print("❌ 数量必须在1-1000之间！")
            except ValueError:
                print("❌ 请输入有效的数字！")
        
        # 获取媒体类型
        print("支持的格式：")
        print("  图片: jpg, png, gif, bmp, webp")
        print("  视频: mp4, avi, mov, wmv, flv, mkv") 
        print("  音频: mp3, wav, flac, aac, m4a")
        print("  文本: txt, json, xml, html, csv")
        
        while True:
            media_type = input("请输入媒体类型 (如: jpg/mp4/mp3/txt): ").strip().lower()
            if media_type:
                break
            print("❌ 媒体类型不能为空！")
        
        # 智能目录管理
        save_dir = self.get_save_directory()
        
        return url, count, media_type, save_dir
    
    def get_save_directory(self):
        """智能获取保存目录"""
        # 默认目录选项
        default_dirs = [
            os.path.join(os.path.expanduser("~"), "Downloads", "API爬虫"),
            os.path.join(os.path.expanduser("~"), "Desktop", "API爬虫"),
            os.path.join(os.getcwd(), "downloads")
        ]
        
        # 如果存在上次使用的目录，优先显示
        if self.last_save_dir and os.path.exists(self.last_save_dir):
            print(f"\n📁 智能目录管理：")
            print(f"1️⃣  使用上次目录: {self.last_save_dir}")
            print(f"2️⃣  选择新目录")
            print(f"3️⃣  使用默认目录: {default_dirs[0]}")
            
            while True:
                choice = input("请选择 (1/2/3): ").strip()
                if choice == '1':
                    return self.last_save_dir
                elif choice == '2':
                    return self.select_new_directory()
                elif choice == '3':
                    save_dir = default_dirs[0]
                    os.makedirs(save_dir, exist_ok=True)
                    return save_dir
                else:
                    print("❌ 请输入有效的选择！")
        else:
            # 没有上次目录，显示简化选项
            print(f"\n📁 选择保存位置：")
            print(f"1️⃣  桌面文件夹: {default_dirs[1]}")
            print(f"2️⃣  下载文件夹: {default_dirs[0]}")
            print(f"3️⃣  当前目录: {default_dirs[2]}")
            print(f"4️⃣  自定义目录")
            
            while True:
                choice = input("请选择 (1/2/3/4): ").strip()
                if choice in ['1', '2', '3']:
                    save_dir = default_dirs[int(choice) - 1] if choice != '3' else default_dirs[2]
                    os.makedirs(save_dir, exist_ok=True)
                    return save_dir
                elif choice == '4':
                    return self.select_new_directory()
                else:
                    print("❌ 请输入有效的选择！")
    
    def select_new_directory(self):
        """选择新目录"""
        print("\n📂 目录选择提示：")
        print("• 直接输入路径，如: C:\\Users\\Downloads")
        print("• 输入 'desktop' 使用桌面目录")
        print("• 输入 'downloads' 使用下载目录")
        
        save_dir = input("请输入保存目录: ").strip()
        
        # 处理快捷命令
        if save_dir.lower() == 'desktop':
            save_dir = os.path.join(os.path.expanduser("~"), "Desktop", "API爬虫")
        elif save_dir.lower() == 'downloads':
            save_dir = os.path.join(os.path.expanduser("~"), "Downloads", "API爬虫")
        
        # 确保目录存在
        os.makedirs(save_dir, exist_ok=True)
        return save_dir

def main():
    """主函数"""
    crawler = APICrawler()
    crawler.print_banner()
    
    while True:
        try:
            # 获取用户输入
            url, count, media_type, save_dir = crawler.get_user_input()
            
            # 创建保存目录
            os.makedirs(save_dir, exist_ok=True)
            print(f"📁 保存目录已创建: {save_dir}")
            
            # 开始爬取
            results = crawler.crawl_api(url, count, media_type, save_dir)
            
            # 显示统计结果
            print("\n" + "=" * 50)
            print("📊 爬取统计：")
            print(f"✅ 成功: {results['success']} 个")
            print(f"❌ 失败: {results['failed']} 个")
            print(f"📁 保存目录: {save_dir}")
            
            if results['files']:
                print(f"📋 文件列表: {len(results['files'])} 个文件")
            
            # 保存最后一次目录
            crawler.last_save_dir = save_dir
            
        except KeyboardInterrupt:
            print("\n\n👋 用户中断操作")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
        
        # 询问是否继续
        print("\n" + "-" * 30)
        continue_choice = input("是否继续爬取? (y/n): ").strip().lower()
        if continue_choice != 'y':
            break
    
    print("\n👋 感谢使用API爬虫工具！")
    print("🌟 如果本工具对您有帮助，请给个Star支持一下！")

if __name__ == "__main__":
    # 检查依赖
    try:
        import requests
    except ImportError:
        print("❌ 缺少依赖库，请先安装: pip install requests")
        sys.exit(1)
    
    main()
