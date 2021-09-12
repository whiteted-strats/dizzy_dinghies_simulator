
for stage=0,2,1 do
    -- Start position
    p = {}
    for i = 0,2,1 do
        v = mainmemory.readfloat(0x109740 + stage * 0xc + i * 0x4, true)
        table.insert(p, v)
    end
    console.log("START:")
    console.log(p)

    console.log("END ABC:")
    for i = 0,2,1 do
        p = {}
        for j = 0,2,1 do
            v = mainmemory.readfloat(0x109e44 + stage * 0x24 + i * 0xc + j * 0x4, true)
            table.insert(p,v)
        end
        console.log(p)
    end
end