
while event.unregisterbyname("input_grabber") do
    --
end

event.onmemoryexecute(function()
	sp = emu.getregister("sp_lo") + 0x80000000
    x_input = mainmemory.read_s16_be(sp + 0x30)
    key_mask = mainmemory.read_u32_be(0x10a118)
    a_press = bit.rshift(bit.band(key_mask, 0x8000), 15)
    if a_press == 1 then
        a_press = "True"
    else
        a_press = "False"
    end
    console.log("(" .. a_press .. "," .. x_input .. "),")

end, 0x80108720, "input_grabber")