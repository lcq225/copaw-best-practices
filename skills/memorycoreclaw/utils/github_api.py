"""
GitHub API Helper for Windows Environment

Windows 环境下 GitHub API 调用工具

问题背景：
- Windows 环境下 Python requests 库可能有 SSL 证书问题
- 导致 API 调用失败，容易被误判为 Token 失效

解决方案：
- 使用 urllib 并禁用 SSL 验证
- 此模块封装了正确的调用方式
"""

import urllib.request
import urllib.error
import ssl
import json
from typing import Optional, Dict, Any


class GitHubAPI:
    """GitHub API 客户端（Windows 兼容）"""
    
    def __init__(self, token: str):
        """
        初始化 GitHub API 客户端
        
        Args:
            token: GitHub Personal Access Token (需要 repo 权限)
        """
        self.token = token
        self.base_url = "https://api.github.com"
        
        # 创建跳过 SSL 验证的上下文
        self.ssl_context = ssl.create_default_context()
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """
        发送 API 请求
        
        Args:
            method: HTTP 方法 (GET, POST, PATCH, DELETE)
            endpoint: API 端点 (如 /repos/owner/repo/releases)
            data: 请求体数据
            
        Returns:
            API 响应数据
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8') if data else None,
            headers=headers,
            method=method
        )
        
        try:
            with urllib.request.urlopen(req, context=self.ssl_context) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else ""
            raise Exception(f"GitHub API Error {e.code}: {error_body}")
    
    def get_user(self) -> Dict:
        """获取当前用户信息"""
        return self._request("GET", "/user")
    
    def get_repo(self, owner: str, repo: str) -> Dict:
        """获取仓库信息"""
        return self._request("GET", f"/repos/{owner}/{repo}")
    
    def create_release(self, owner: str, repo: str, tag: str, name: str, 
                       body: str, draft: bool = False, prerelease: bool = False) -> Dict:
        """
        创建 Release
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            tag: Tag 名称
            name: Release 标题
            body: Release 内容
            draft: 是否为草稿
            prerelease: 是否为预发布
            
        Returns:
            创建的 Release 信息
        """
        data = {
            "tag_name": tag,
            "name": name,
            "body": body,
            "draft": draft,
            "prerelease": prerelease
        }
        return self._request("POST", f"/repos/{owner}/{repo}/releases", data)
    
    def list_releases(self, owner: str, repo: str) -> list:
        """列出所有 Releases"""
        return self._request("GET", f"/repos/{owner}/{repo}/releases")
    
    def delete_release(self, owner: str, repo: str, release_id: int) -> bool:
        """删除 Release"""
        try:
            self._request("DELETE", f"/repos/{owner}/{repo}/releases/{release_id}")
            return True
        except Exception:
            return False
    
    def create_issue(self, owner: str, repo: str, title: str, body: str = "", 
                     labels: list = None) -> Dict:
        """创建 Issue"""
        data = {
            "title": title,
            "body": body,
            "labels": labels or []
        }
        return self._request("POST", f"/repos/{owner}/{repo}/issues", data)


# 使用示例
if __name__ == "__main__":
    import os
    
    # 从环境变量或直接设置 Token
    token = os.environ.get("GITHUB_TOKEN", "your-token-here")
    
    api = GitHubAPI(token)
    
    # 测试 Token
    try:
        user = api.get_user()
        print(f"Token valid! User: {user.get('login')}")
    except Exception as e:
        print(f"Token invalid: {e}")