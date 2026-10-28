# vmos-cloud

Agent skill：通过 VMOS Cloud OpenAPI 操作云手机（无需开启 ADB）。适用于 Hermes Agent、Claude Code 等支持 `SKILL.md` 的 agent。

能力：查看设备状态、截图、读取界面元素、点击 / 滑动 / 输入 / 按键、启动应用、打开链接、安装 APK、执行 shell，以及代理、GPS、时区等设备级接口的透传调用。

## 安装

```sh
git clone git@github.com:sailtonight/vmos-cloud.git ~/.agents/skills/vmos-cloud
ln -sfn ../../.agents/skills/vmos-cloud ~/.hermes/skills/vmos-cloud   # Hermes
ln -sfn ../../.agents/skills/vmos-cloud ~/.claude/skills/vmos-cloud   # Claude Code
```

## 配置

VMOS Cloud 控制台 → Developer → API 获取 AccessKeyID / SecretAccessKey：

```sh
mkdir -p ~/.config/vmos && cat > ~/.config/vmos/credentials <<'CRED'
VMOS_AK=...
VMOS_SK=...
VMOS_PAD=...   # 可选，默认 padCode
CRED
chmod 600 ~/.config/vmos/credentials
```

## 使用

```sh
python3 scripts/vmos.py status
python3 scripts/vmos.py shot
python3 scripts/vmos.py ui
python3 scripts/vmos.py tap --text 搜索
python3 scripts/vmos.py text "lipstick" && python3 scripts/vmos.py key enter
```

完整命令与操作规范见 [SKILL.md](SKILL.md)，接口索引见 [references/api.md](references/api.md)。
