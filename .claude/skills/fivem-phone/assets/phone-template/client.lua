-- Phone template client: open/close, NUI focus, walking while open, prop + animation, auto-close, fold.
-- Sources for the patterns: references/phone-frame.md (npwd and qb-phone source).

local isOpen = false
local folded = true
local keepInput = true
local prop = nil

local PROP_MODEL = `prop_amb_phone`
local VALID_DEVICES = { bar = true, passport = true, wide = true, tall = true, flip = true, trifold = true }
local DICT_FOOT, DICT_CAR = 'cellphone@', 'anim@cellphone@in_car@ps'

-- ───────── helpers ─────────
local function loadModel(model)
    if HasModelLoaded(model) then return true end
    RequestModel(model)
    local timeout = GetGameTimer() + 3000
    while not HasModelLoaded(model) and GetGameTimer() < timeout do Wait(0) end
    return HasModelLoaded(model)
end

local function loadDict(dict)
    if HasAnimDictLoaded(dict) then return true end
    RequestAnimDict(dict)
    local timeout = GetGameTimer() + 3000
    while not HasAnimDictLoaded(dict) and GetGameTimer() < timeout do Wait(0) end
    return HasAnimDictLoaded(dict)
end

local function currentDict(ped)
    return IsPedInAnyVehicle(ped, false) and DICT_CAR or DICT_FOOT
end

local function deleteProp()
    if prop and DoesEntityExist(prop) then DeleteEntity(prop) end
    prop = nil
end

local function attachProp()
    deleteProp()
    if not loadModel(PROP_MODEL) then return end
    local ped = PlayerPedId()
    local c = GetEntityCoords(ped)
    prop = CreateObject(PROP_MODEL, c.x, c.y, c.z + 0.2, true, true, false)
    AttachEntityToEntity(prop, ped, GetPedBoneIndex(ped, 28422), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, true, true, false, false, 2, true)
    SetModelAsNoLongerNeeded(PROP_MODEL)
end

local function playAnim(name)
    local ped = PlayerPedId()
    local dict = currentDict(ped)
    if loadDict(dict) then
        TaskPlayAnim(ped, dict, name, 3.0, 3.0, -1, 50, 0, false, false, false)
    end
end

local function stopAnims()
    local ped = PlayerPedId()
    StopAnimTask(ped, DICT_FOOT, 'cellphone_text_in', 2.5)
    StopAnimTask(ped, DICT_CAR, 'cellphone_text_in', 2.5)
    RemoveAnimDict(DICT_FOOT)
    RemoveAnimDict(DICT_CAR)
end

local function clock()
    return ('%02d:%02d'):format(GetClockHours(), GetClockMinutes())
end

-- Replace with your framework's checks (QBCore metadata isdead/inlaststand/ishandcuffed, an item check …)
local function canOpen()
    local ped = PlayerPedId()
    return not IsPauseMenuActive() and not IsPedDeadOrDying(ped, true) and not IsPedCuffed(ped) and not IsPedRagdoll(ped)
end

-- ───────── open / close ─────────
local close

local function open()
    if isOpen or not canOpen() then return end
    isOpen, keepInput = true, true
    SetNuiFocus(true, true)
    SetNuiFocusKeepInput(true)
    attachProp()
    playAnim('cellphone_text_in')
    SendNUIMessage({
        action = 'open',
        clock = clock(),
        fold = folded and 'closed' or 'open',
        device = (Config.AllowDeviceChange and GetResourceKvpString('phone:device')) or Config.Device,
        allowDeviceChange = Config.AllowDeviceChange,
        lockScreen = Config.LockScreen,
        theme = GetResourceKvpString('phone:theme') or 'dark',
        scale = tonumber(GetResourceKvpString('phone:scale') or '') or 0.85,
    })

    -- disable the keys that would fight the phone (npwd's list, trimmed); only while open
    CreateThread(function()
        while isOpen do
            if keepInput then
                DisableControlAction(0, 1, true)    -- look left/right
                DisableControlAction(0, 2, true)    -- look up/down
                DisableControlAction(0, 24, true)   -- attack
                DisableControlAction(0, 25, true)   -- aim
                DisableControlAction(0, 37, true)   -- weapon wheel
                DisableControlAction(0, 16, true)   -- next weapon
                DisableControlAction(0, 17, true)   -- previous weapon
                DisableControlAction(0, 140, true)  -- melee light
                DisableControlAction(0, 199, true)  -- pause menu (P)
                DisableControlAction(0, 200, true)  -- pause menu (ESC)
                DisableControlAction(0, 245, true)  -- chat
                DisableControlAction(0, 322, true)  -- ESC
            end
            Wait(0)
        end
    end)

    -- slow watcher: auto-close, keep the animation playing, update the clock
    CreateThread(function()
        local lastClock = clock()
        while isOpen do
            local ped = PlayerPedId()
            if IsPauseMenuActive() or IsPedDeadOrDying(ped, true) or IsPedCuffed(ped) then
                close()
                break
            end
            local dict = currentDict(ped)
            if not IsEntityPlayingAnim(ped, dict, 'cellphone_text_in', 3) then playAnim('cellphone_text_in') end
            local now = clock()
            if now ~= lastClock then
                lastClock = now
                SendNUIMessage({ action = 'clock', clock = now })
            end
            Wait(250)
        end
    end)
end

close = function()
    if not isOpen then return end
    isOpen = false
    SendNUIMessage({ action = 'close' })
    SetNuiFocus(false, false)
    SetNuiFocusKeepInput(false)
    playAnim('cellphone_text_out')
    SetTimeout(450, function()
        if isOpen then return end -- reopened in the meantime
        stopAnims()
        deleteProp()
    end)
end

RegisterCommand('phone', function() if isOpen then close() else open() end end, false)
RegisterKeyMapping('phone', 'Open phone', 'keyboard', Config.OpenKey or 'F1')

-- ───────── NUI callbacks (always call cb) ─────────
RegisterNUICallback('close', function(_, cb) close(); cb({}) end)

RegisterNUICallback('keepInput', function(data, cb)
    keepInput = data and data.value == true
    if isOpen then SetNuiFocusKeepInput(keepInput) end -- off while typing, so "w" doesn't walk
    cb({})
end)

RegisterNUICallback('fold', function(data, cb)
    folded = data and data.folded == true
    cb({})
end)

RegisterNUICallback('settings', function(data, cb)
    if type(data) == 'table' then
        if data.theme == 'dark' or data.theme == 'light' then SetResourceKvp('phone:theme', data.theme) end
        local s = tonumber(data.scale)
        if s and s >= 0.65 and s <= 1.0 then SetResourceKvp('phone:scale', tostring(s)) end
        if Config.AllowDeviceChange and VALID_DEVICES[data.device] then SetResourceKvp('phone:device', data.device) end
    end
    cb({})
end)

-- Data goes to the server; the page only sends intent. lib.callback is from ox_lib.
local function proxy(name)
    RegisterNUICallback(name, function(data, cb)
        local ok, result = pcall(lib.callback.await, 'phone:' .. name, false, data)
        cb(ok and result or { ok = false, error = 'server' })
    end)
end
proxy('messages:threads')
proxy('messages:thread')
proxy('messages:send')
proxy('wallet:get')
proxy('wallet:transfer')

-- Server pushes
RegisterNetEvent('phone:client:message', function(threadId, message)
    SendNUIMessage({ action = 'message', threadId = threadId, message = message })
    if not isOpen then SendNUIMessage({ action = 'notify', title = message.from or '信息', text = message.text, app = 'messages' }) end
end)

RegisterNetEvent('phone:client:notify', function(title, text, app)
    SendNUIMessage({ action = 'notify', title = title, text = text, app = app })
end)

-- ───────── cleanup ─────────
AddEventHandler('onResourceStop', function(res)
    if res ~= GetCurrentResourceName() then return end
    if isOpen then
        SetNuiFocus(false, false)
        SetNuiFocusKeepInput(false)
    end
    stopAnims()
    deleteProp()
end)
