
function readPtr(addr)
    assert(mainmemory.read_u8(addr) == 0x80)
    local p = mainmemory.read_u32_be(addr)
    return p - 0x80000000
end

function verifyGridAndGetFinishOffset(xSize, zSize, PLI_base, polyMasterList)
    -- We don't care for using the structure except to extract everything
    --   (does assume there are no bugs in how they find relevant collision)

    -- We verify that all items in the master list appear exactly once in the grid,
    --   and so just return the finishOffset (effectively the length of the list)
    slices = {}

    for i = 0,xSize*zSize-1,1 do
        polyListInfo = PLI_base + i * 8
        startOffset = mainmemory.read_s32_be(polyListInfo + 0x0)
        count = mainmemory.read_s16_be(polyListInfo + 0x4)

        poly = polyMasterList + 2*startOffset

        for j = 0,count-1,1 do
            header = mainmemory.read_u16_be(poly + 0x0)
            pointCount = bit.rshift(header, 0xe) + 2
            u16_length = pointCount + 1
            poly = poly + u16_length*2
        end

        finishOffset = bit.rshift(poly - polyMasterList, 1)
        
        if count > 0 then
            table.insert(slices, {startOffset, finishOffset})
        end
    end

    function order(p1,p2)
        return p1[1] < p2[1]
    end

    table.sort(slices, order)

    prev = 0
    for _, slice in ipairs(slices) do
        a = slice[1]
        b = slice[2]
        assert(prev == a)
        prev = b
    end

    finishOffset = prev
    return finishOffset
end



-- param_1 for findAllCollision [at 80021c14] = *(&PTR_800ec1c0)[DAT_800eb734]->field_0x40
DAT_800eb734 = mainmemory.readbyte(0x0eb734)
assert(DAT_800eb734 == 0)
obj = readPtr(0x0ec1c0 + DAT_800eb734 * 4)
field_40 = readPtr(obj + 0x40)
param_1 = mainmemory.read_s16_be(field_40)

-- Read the 'peak' to give us the pointList and our gridTop
peak = readPtr(0x0d03f8) + 0xc0 * param_1
pointList = readPtr(readPtr(peak + 0x64) + 0x50)
gridIndex = mainmemory.read_s16_be(peak + 0x10)
gridTop = readPtr(0x0d1104) + gridIndex * 0x24

-- Read grid properties
xSize = mainmemory.read_s32_be(gridTop + 0x0)
zSize = mainmemory.read_s32_be(gridTop + 0x4)
PLI_base = readPtr(gridTop + 0x20)
polyMasterList = readPtr(gridTop + 0x10)

-- Check the grid is, to our mind, just a jumbled version of the list, and get the length
finishOffset = verifyGridAndGetFinishOffset(xSize, zSize, PLI_base, polyMasterList)


-- Dump out all the polys
endPoly = polyMasterList + finishOffset*2
poly = polyMasterList

file = io.open("polys.txt", "w")
io.output(file)

polyCount = 0
while poly ~= endPoly do
    polyCount = polyCount + 1
    header = mainmemory.read_u16_be(poly + 0x0)
    pointCount = bit.rshift(header, 0xe) + 2
    assert(pointCount == 3 or pointCount == 4)
    io.write("[\n")
    for o = 1,pointCount,1 do
        pI = mainmemory.read_s16_be(poly + 0x2*o)
        pnt = pointList + pI * 0x6
        x = mainmemory.read_s16_be(pnt + 0x0)
        y = mainmemory.read_s16_be(pnt + 0x2)
        z = mainmemory.read_s16_be(pnt + 0x4)
        io.write("  (" .. x .. "," .. y .. "," .. z .. "),\n")
    end
    io.write("],\n")

    poly = poly + 2 * pointCount + 2
end 

io.close()

console.log("Dumped " .. polyCount .. " polys")