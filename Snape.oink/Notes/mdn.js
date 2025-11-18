console.log("Web Launched");

function draw() {
  const board = /** @type {HTMLCanvasElement}*/ (
    document.querySelector("#board")
  );
  console.log(board);

  const ctx = board.getContext("2d");
  console.log(ctx);

  // ctx.fillStyle("white")
  ctx.fillRect(20, 20, 100, 100);
  ctx.clearRect(30, 30, 80, 80);
  ctx.strokeRect(40, 40, 60, 60);

  ctx.beginPath();
  ctx.moveTo(175, 50);
  ctx.lineTo(200, 25);

  ctx.lineTo(200, 75);
  ctx.closePath();
  // ctx.fill();
  ctx.stroke();

  ctx.beginPath();
  ctx.moveTo(150, 75);
  ctx.arc(150, 75, 10, 0 * (Math.PI / 180), 60 * (Math.PI / 180), false);
  // ctx.fill()
  ctx.strokeStyle = "#f34343";
  ctx.stroke();

  const circle = new Path2D();
  ctx.fillStyle = "#f20a0aff";
  circle.arc(250, 35, 25, 0, 2 * Math.PI);
  ctx.fill(circle);

  for (let i = 0; i < 6; i++) {
    for (let j = 0; j < 6; j++) {
      ctx.fillStyle = `rgb(${Math.floor(255 - 42.5 * i)} ${Math.floor(
        255 - 42.5 * j
      )} 0)`;
      ctx.fillRect(j * 25, i * 25 + 200, 25, 25);
    }
  }
}

draw();
