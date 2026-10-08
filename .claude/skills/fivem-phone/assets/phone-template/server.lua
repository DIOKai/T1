-- Phone template server: the server decides. The page only asks.
-- Framework calls checked against source (2026-10):
--   qb-core  server/functions.lua: QBCore.Functions.GetPlayer, GetPlayerByPhone (charinfo.phone)
--   qbx_core server/functions.lua: exports GetPlayer, GetPlayerByPhone; server/player.lua: exports AddMoney/RemoveMoney/GetMoney
--   qb-core config: Money.DontAllowMinus = { 'cash', 'crypto' } → BANK CAN GO NEGATIVE, so check the balance yourself.
-- Storage below is in memory to keep the template self-contained. Replace the TODOs with oxmysql tables.

local QBX = GetResourceState('qbx_core') == 'started'
local QBCore = not QBX and exports['qb-core']:GetCoreObject() or nil

local Bridge = {}
function Bridge.player(src) return QBX and exports.qbx_core:GetPlayer(src) or QBCore.Functions.GetPlayer(src) end
function Bridge.byPhone(number) return QBX and exports.qbx_core:GetPlayerByPhone(number) or QBCore.Functions.GetPlayerByPhone(number) end
function Bridge.bank(p) return p.PlayerData.money.bank or 0 end
function Bridge.removeBank(p, amount, reason)
    if QBX then return exports.qbx_core:RemoveMoney(p.PlayerData.source, 'bank', amount, reason) end
    return p.Functions.RemoveMoney('bank', amount, reason)
end
function Bridge.addBank(p, amount, reason)
    if QBX then return exports.qbx_core:AddMoney(p.PlayerData.source, 'bank', amount, reason) end
    return p.Functions.AddMoney('bank', amount, reason)
end

-- ───────── guards ─────────
local lastCall, busy = {}, {}
local function rateLimited(src, key, ms)
    local k = src .. key
    local now = GetGameTimer()
    if lastCall[k] and now - lastCall[k] < ms then return true end
    lastCall[k] = now
    return false
end
AddEventHandler('playerDropped', function()
    local src = source
    busy[src] = nil
    for k in pairs(lastCall) do if k:find('^' .. src .. '%D') then lastCall[k] = nil end end
end)

-- ───────── demo storage (TODO: oxmysql) ─────────
local txByCid = {}       -- citizenid → { {title, time, amount}, … }
local function clock() return os.date('%H:%M') end
local function addTx(cid, title, amount)
    txByCid[cid] = txByCid[cid] or {}
    table.insert(txByCid[cid], 1, { title = title, time = clock(), amount = amount })
    if #txByCid[cid] > 50 then table.remove(txByCid[cid]) end
end

-- ───────── messages ─────────
lib.callback.register('phone:messages:threads', function(src)
    local p = Bridge.player(src)
    if not p then return { ok = false } end
    return { ok = true, threads = {} } -- TODO: SELECT threads WHERE citizenid = p.PlayerData.citizenid
end)

lib.callback.register('phone:messages:thread', function(src, data)
    local p = Bridge.player(src)
    if not p or type(data) ~= 'table' or type(data.id) ~= 'number' then return { ok = false } end
    return { ok = true, messages = {} } -- TODO: check the thread belongs to this citizenid, then load it
end)

lib.callback.register('phone:messages:send', function(src, data)
    local p = Bridge.player(src)
    if not p or type(data) ~= 'table' or type(data.text) ~= 'string' or type(data.threadId) ~= 'number' then
        return { ok = false, error = '无效请求' }
    end
    if rateLimited(src, 'msg', 500) then return { ok = false, error = '发太快了' } end
    local text = data.text:gsub('^%s+', ''):gsub('%s+$', '')
    if #text == 0 or #text > 1500 then return { ok = false, error = '信息长度不对' } end -- bytes; ~500 CJK chars
    -- TODO: look up the thread for THIS citizenid, find the other participant's phone number,
    --       insert the message, and if they are online: TriggerClientEvent('phone:client:message', targetSrc, threadId, msg)
    return { ok = true, message = { id = os.time(), out = true, text = text, time = clock() } }
end)

-- ───────── wallet ─────────
lib.callback.register('phone:wallet:get', function(src)
    local p = Bridge.player(src)
    if not p then return { ok = false } end
    return { ok = true, balance = Bridge.bank(p), tx = txByCid[p.PlayerData.citizenid] or {} }
end)

local MAX_TRANSFER = 1000000

lib.callback.register('phone:wallet:transfer', function(src, data)
    if type(data) ~= 'table' then return { ok = false, error = '无效请求' } end
    local amount, to = tonumber(data.amount), tostring(data.to or '')
    if not amount or amount ~= math.floor(amount) or amount < 1 or amount > MAX_TRANSFER then
        return { ok = false, error = '金额不正确' }
    end
    if not to:match('^%d+$') or #to < 3 or #to > 10 then return { ok = false, error = '电话号码不正确' } end
    if busy[src] or rateLimited(src, 'tx', 3000) then return { ok = false, error = '请稍等再试' } end

    busy[src] = true -- one transfer at a time per player (no double-spend by spamming)
    local ok, result = pcall(function()
        local sender = Bridge.player(src)
        local target = Bridge.byPhone(to)
        if not sender then return { ok = false, error = '无效玩家' } end
        if not target then return { ok = false, error = '找不到这个号码（对方要在线）' } end
        if target.PlayerData.source == src then return { ok = false, error = '不能转给自己' } end
        if Bridge.bank(sender) < amount then return { ok = false, error = '余额不足' } end
        if not Bridge.removeBank(sender, amount, 'phone-transfer') then return { ok = false, error = '扣款失败' } end
        if not Bridge.addBank(target, amount, 'phone-transfer') then
            Bridge.addBank(sender, amount, 'phone-transfer-refund') -- roll back
            return { ok = false, error = '转账失败，已退回' }
        end
        local fromPhone = sender.PlayerData.charinfo.phone
        addTx(sender.PlayerData.citizenid, ('转账 · %s'):format(to), -amount)
        addTx(target.PlayerData.citizenid, ('收款 · %s'):format(fromPhone), amount)
        print(('[phone] transfer %s (%s) -> %s (%s): $%d'):format(sender.PlayerData.citizenid, src, target.PlayerData.citizenid, target.PlayerData.source, amount))
        TriggerClientEvent('phone:client:notify', target.PlayerData.source, '收到转账', ('$%d 来自 %s'):format(amount, fromPhone), 'wallet')
        return { ok = true, balance = Bridge.bank(sender) }
    end)
    busy[src] = nil
    if not ok then print('[phone] transfer error: ' .. tostring(result)) return { ok = false, error = '伺服器错误' } end
    return result
end)
