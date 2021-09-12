require "lua_input"

local playStateAddr = mainmemory.read_u32_be(0x0ebde0) - 0x80000000
local timerAddr = 0x0eb914
local turnBufferAddr = 0x109e08

local t = 0

function advance()
    local playState = mainmemory.read_u8(playStateAddr)
    if playState == 3 then
        return false    -- finished
    end

    if t == 0 then
        return playState == 2   -- first frame, timer stays on 0
    else
        local timer = mainmemory.read_u16_be(timerAddr)
        return timer == t       -- timer caught up = time to advance
    end
end


function onUpdateEnd()
    local timer = mainmemory.read_u16_be(timerAddr)
    if timer <= 0 then
        return
    end

    struct = mainmemory.read_u32_be(0x12818C) - 0x80000000
    local angle = mainmemory.readfloat(struct + 0x3c, true)
    
    local x = mainmemory.readfloat(0x128148, true)
    local z = mainmemory.readfloat(0x128150, true)

    -- Dump the sum of the turn buffer
    local s = 0
    for i = 0,19,1 do
        s = s + mainmemory.read_s16_be(turnBufferAddr + 0x2*i)
    end
    --console.log(s)
end

while event.unregisterbyname("onUpdateEnd") do
    --
end

event.onmemoryexecute(onUpdateEnd, 0x80108e28, "onUpdateEnd")

while true do
    gui.drawText(10,15,"frame #" .. t)

    input = inputs[t+1]    -- fuck lua
    press_A = input[1]
    analogue_x = input[2]

    frame_input = {
        ["P1 A"] = press_A,
    }
    joypad.set(frame_input)
    
    frame_input = {
        ["P1 X Axis"] = analogue_x,
    }
    joypad.setanalog(frame_input)

    emu.frameadvance()
    if advance() then
        t = t + 1

        -- Bad place to log out info!
        -- The timer seems to update long before, so sometimes we miss the frame
    end
end