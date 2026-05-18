// =========================
// static/teacher.js
// =========================

const socket = io()

const canvas =
document.getElementById(
    "canvas"
)

const ctx =
canvas.getContext("2d")

const GRID_SIZE = 16

let floorplans = []

let current = null

let currentType =
"danger"

let polygon = []

let drawing = false

let zones = []


// =========================
// LOAD FLOORPLANS
// =========================

fetch("/floorplans")

.then(r => r.json())

.then(data => {

    floorplans = data

    const select =
    document.getElementById(
        "building"
    )

    data.forEach(fp => {

        const option =
        document.createElement(
            "option"
        )

        option.value = fp.name

        option.innerText = fp.name

        select.appendChild(option)
    })

    current = data[0]

    draw()
})


// =========================
// BUILDING SWITCH
// =========================

document
.getElementById("building")
.addEventListener(
    "change",
    e => {

        current = floorplans.find(

            f => f.name ===
            e.target.value
        )

        draw()
    }
)


// =========================
// SAFE BUTTON
// =========================

document
.getElementById("safe")
.onclick = () => {

    currentType = "safe"
}


// =========================
// DANGER BUTTON
// =========================

document
.getElementById("danger")
.onclick = () => {

    currentType = "danger"
}


// =========================
// DRAWING
// =========================

canvas.addEventListener(
    "mousedown",
    () => {

        polygon = []

        drawing = true
    }
)

canvas.addEventListener(
    "mousemove",
    e => {

        if(!drawing) return

        const rect =
        canvas.getBoundingClientRect()

        polygon.push([

            e.clientX - rect.left,

            e.clientY - rect.top
        ])

        draw()
    }
)

canvas.addEventListener(
    "mouseup",
    () => {

        drawing = false

        const zone = {

            building:
            current.name,

            type:
            currentType,

            points:
            polygon
        }

        zones.push(zone)

        socket.emit(
            "zone_update",
            zone
        )

        draw()
    }
)


// =========================
// RECEIVE LIVE ZONES
// =========================

socket.on(
    "zone_sync",
    zone => {

        zones.push(zone)

        draw()
    }
)


// =========================
// DRAW EVERYTHING
// =========================

function draw(){

    ctx.clearRect(
        0,
        0,
        800,
        800
    )

    if(!current) return


    // =====================
    // GRID
    // =====================

    ctx.strokeStyle =
    "#d0d0d0"

    ctx.lineWidth = 1

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


    // =====================
    // WALLS
    // =====================

    ctx.fillStyle = "black"

    current.walls.forEach(w => {

        ctx.fillRect(

            w[0] * GRID_SIZE,

            w[1] * GRID_SIZE,

            GRID_SIZE,

            GRID_SIZE
        )
    })


    // =====================
    // EXITS
    // =====================

    ctx.fillStyle = "lime"

    current.exits.forEach(ex => {

        ctx.fillRect(

            ex[0] * GRID_SIZE,

            ex[1] * GRID_SIZE,

            GRID_SIZE,

            GRID_SIZE
        )
    })


    // =====================
    // SAVED ZONES
    // =====================

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
            "green"
        }

        ctx.lineWidth = 3

        ctx.fill()

        ctx.stroke()
    })


    // =====================
    // ACTIVE DRAW
    // =====================

    if(polygon.length > 0){

        ctx.beginPath()

        polygon.forEach((p, i) => {

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

        ctx.strokeStyle =

            currentType === "danger"

            ?

            "red"

            :

            "green"

        ctx.lineWidth = 4

        ctx.stroke()
    }
}