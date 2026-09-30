"""bbcli — CUHK-SZ Blackboard 只读 CLI 连接器。

分层：config（路径与配置）/ transport（curl_cffi 会话与 TLS 指纹）/
auth（ADFS OAuth2 登录）/ api（Learn REST 封装）/ cli（命令面）。
纪律：只读——不出任何写操作请求；凭据与会话只落用户目录，不进任何仓库。
"""

__version__ = "0.1.1"
