Config = {}

-- Device style: 'bar' | 'passport' (iPhone Duo-like) | 'wide' (Fold8-like) | 'tall' (Fold8 Ultra-like)
--               'flip' (Flip8-like) | 'trifold' (TriFold-like). See references/real-foldables.md.
Config.Device = 'wide'
Config.AllowDeviceChange = true   -- players can pick another style in Settings (saved per player with KVP)
Config.LockScreen = true          -- show the lock screen each time the phone is opened
Config.OpenKey = 'F1'             -- default key; players can rebind it in GTA settings → Key Bindings → FiveM
