# ABN 企业查询（ABN Lookup）

一个 [Dify](https://dify.ai) 工具插件：通过澳大利亚商业登记局（ABR）官方 **ABN Lookup API** 查询澳洲企业信息，并提供本地的 ACN→ABN 换算工具。

## 工具

### 1. ABN 企业信息查询（ABN Lookup）

用 **ABN（11 位）** 或 **ACN（9 位）** 查询，返回：

- 注册主体名称（公司名，或个人/个体户的法定姓名）
- 该 ABN 下登记的经营名称（business name）
- 主体状态（Active / Cancelled）
- 主体类型（如 Australian Public Company、Sole Trader）
- GST 注册状态及生效日期
- 注册地址的州与邮编
- 可选：历史记录（曾用名、状态变更）

传入 9 位 ACN 时，插件会在本地推导出对应 ABN（ABN 的后 9 位即为 ACN）再查询。

### 2. ACN 转 ABN 换算（ACN to ABN Converter）

把 9 位 ACN 换算成等价的 11 位 ABN，并校验两个号码的校验位。纯本地计算，不调用 API、不需要凭据。

## 凭据配置

`ABN Lookup` 工具需要 **ABN Lookup API key**：

1. 在 ABR 开发者门户注册：<https://api.abn.business.gov.au>
2. 订阅免费的 **ABN Lookup Keys** 产品并创建密钥。
3. 在 Dify 中打开 **工具 → ABN Lookup → 授权**，把密钥粘贴到 `ABN Lookup API key` 输入框。

密钥会以 `x-vr-key` 请求头发送。`ACN to ABN` 工具无需任何凭据。

## 使用方法

1. 从 Dify Marketplace 安装插件（或用 *从本地文件安装* 安装 `.difypkg` 包）。
2. 用 ABN Lookup API key 完成授权。
3. 在 Agent 或工作流节点中添加任一工具，例如传入 `51824753556` 查询该 ABN 的企业信息。

## 数据与隐私

见 [PRIVACY.md](../PRIVACY.md)：本插件只把你传入的 ABN/ACN 转发给 ABR 官方接口并返回结果，不存储、不外发到任何第三方。

## 源码

<https://github.com/Ellan1989/dify-abn-lookup>

## 许可

Apache-2.0
