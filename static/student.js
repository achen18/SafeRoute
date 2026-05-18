// =========================
// static/student.js
// =========================

const socket = io()

const canvas =
document.getElementById("canvas")

const ctx =
canvas.getContext("2d")

const GRID_SIZE = 16

let floorplans = []

let current = null

let student = null

let path = []

let zones = []


// =========================
// INIT
// =========================

async function init(){

    // LOAD FLOORPLANS

    const fpResponse =
    await fetch("/floorplans")

    floorplans =
    await fpResponse.json()

    const select =
    document.getElementById(
        "building"
    )

    floorplans.forEach(fp => {

        const option =
        document.createElement("option")

        option.value = fp.name

        option.innerText = fp.name

        select.appendChild(option)
    })

    current = floorplans[0]


    // LOAD EXISTING ZONES

    const zoneResponse =
    await fetch("/zones")

    const zoneData =
    await zoneResponse.json()

    zones = []

    Object.values(zoneData).forEach(arr => {

        arr.forEach(z => {

            zones.push(z)
        })
    })

    draw()
}

init()


// =========================
// BUILDING SWITCH
// =========================

document
.getElementById("building")
.addEventListener(
    "change",
    e => {

        current =
        floorplans.find(

            f => f.name ===
            e.target.value
        )

        draw()
    }
)


// =========================
// CLICK TO PLACE STUDENT
// =========================

canvas.addEventListener(
    "click",
    async e => {

        const rect =
        canvas.getBoundingClientRect()

        const x = Math.floor(

            (
                e.clientX -
                rect.left
            ) / GRID_SIZE
        )

        const y = Math.floor(

            (
                e.clientY -
                rect.top
            ) / GRID_SIZE
        )

        student = [x,y]

        await calculateRoute()

        draw()
    }
)


// =========================
// SOCKET RECEIVE
// =========================

socket.on(
    "zone_sync",
    async zone => {

        console.log("ZONE RECEIVED")
        console.log(zone)

        zones.push(zone)

        if(
            student &&
            zone.building === current.name
        ){

            await calculateRoute()
        }

        draw()
    }
)


// =========================
// ROUTE
// =========================

async function calculateRoute(){

    const response =
    await fetch(
        "/route",
        {

            method:"POST",

            headers:{

                "Content-Type":
                "application/json"
            },

            body:JSON.stringify({

                building:
                current.name,

                start:
                student
            })
        }
    )

    path =
    await response.json()
}


// =========================
// DRAW
// =========================

function draw(){

    ctx.clearRect(
        0,
        0,
        canvas.width,
        canvas.height
    )

    if(!current) return


    // GRID

    ctx.strokeStyle =
    "#d0d0d0"

    for(let x = 0; x < 800; x += GRID_SIZE){

        ctx.beginPath()

        ctx.moveTo(x,0)

        ctx.lineTo(x,800)

        ctx.stroke()
    }

    for(let y = 0; y < 800; y += GRID_SIZE){

        ctx.beginPath()

        ctx.moveTo(0,y)

        ctx.lineTo(800,y)

        ctx.stroke()
    }


    // ZONES

    zones.forEach(z => {

        if(
            z.building !== current.name
        ){
            return
        }

        ctx.beginPath()

        z.points.forEach((p, i) => {

            if(i === 0){

                ctx.moveTo(
                    p[0],
                    p[1]
                )

            }else{

                ctx.lineTo(
                    p[0],
                    p[1]
                )
            }
        })

        ctx.closePath()

        if(z.type === "danger"){

            ctx.fillStyle =
            "rgba(255,0,0,0.4)"

            ctx.strokeStyle =
            "red"

        }else{

            ctx.fillStyle =
            "rgba(0,255,0,0.4)"

            ctx.strokeStyle =
            "lime"
        }

        ctx.lineWidth = 4

        ctx.fill()

        ctx.stroke()
    })


    // WALLS

    ctx.fillStyle = "black"

    current.walls.forEach(w => {

        ctx.fillRect(

            w[0] * GRID_SIZE,

            w[1] * GRID_SIZE,

            GRID_SIZE,

            GRID_SIZE
        )
    })


    // EXITS

    ctx.fillStyle = "lime"

    current.exits.forEach(ex => {

        ctx.fillRect(

            ex[0] * GRID_SIZE,

            ex[1] * GRID_SIZE,

            GRID_SIZE,

            GRID_SIZE
        )
    })


    // PATH

    ctx.fillStyle =
    "purple"

    path.forEach(p => {

        ctx.fillRect(

            p[0] * GRID_SIZE + 4,

            p[1] * GRID_SIZE + 4,

            GRID_SIZE - 8,

            GRID_SIZE - 8
        )
    })


    // STUDENT

    if(student){

        ctx.fillStyle =
        "blue"

        ctx.fillRect(

            student[0] * GRID_SIZE,

            student[1] * GRID_SIZE,

            GRID_SIZE,

            GRID_SIZE
        )
    }
}