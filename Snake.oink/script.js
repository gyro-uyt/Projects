console.log("Script loaded");

// varaibles
const startButton = document.querySelector("#start");
const stopButton = document.querySelector("#stop");
const board = /** @type {HTMLCanvasElement}*/ (
  document.querySelector("#board")
);
const ctx = board.getContext("2d");
const boxSize = 20;
let food_x;
let food_y;
let snakeBody = [{ x: 5, y: 5 }];
let dir = "right"; // default direction, when game starts
let gameInterval;
let isCollision = false;

window.addEventListener("keydown", (e) => {
  console.log(e.key);
  if (e.key == "ArrowUp") dir = "up";
  if (e.key == "ArrowDown") dir = "down";
  if (e.key == "ArrowRight") dir = "right";
  if (e.key == "ArrowLeft") dir = "left";
});

function gameBackground() {
  for (let i = 0; i < 20; i++) {
    for (let j = 0; j < 20; j++) {
      ctx.strokeRect(i * boxSize + 1, j * boxSize + 1, 20 - 2, 20 - 2);
    }
  }
}

function spawnFood() {
  food_x = Math.floor(Math.random() * 20);
  food_y = Math.floor(Math.random() * 20);
}
spawnFood();

function drawSnakeAndFood(i, j) {
  ctx.fillStyle = "#0fe236ff";
  snakeBody.forEach((element) => {
    ctx.fillRect(element.x * boxSize, element.y * boxSize, boxSize, boxSize);
  });
  ctx.fillStyle = "#ff00ddff";
  ctx.fillRect(food_x * boxSize, food_y * boxSize, boxSize, boxSize);
}

function updateSnake() {
  let head = { ...snakeBody[0] }; // makes a new copy {x,y} object with the same values as the current head, so that operation on it doesn't affects original array
  // let head = snakeBody[0]; // head & snakeBody[0] both points to same object in the head, When you do head.x++ or head.y--, you’re directly mutating the existing head in the array.
  if (dir === "up") head.y--;
  if (dir === "down") head.y++;
  if (dir === "right") head.x++;
  if (dir === "left") head.x--;

  snakeBody.unshift(head);

  // body collision
  for (let i = 1; i < snakeBody.length; i++) {
    if (head.x === snakeBody[i].x && head.y === snakeBody[i].y)
      isCollision = true;
  }
  // boundary collision
  if (head.x > 19 || head.x < 0 || head.y < 0 || head.y > 19)
    isCollision = true;

  collision(isCollision);

  if (head.x === food_x && head.y === food_y) spawnFood();
  else snakeBody.pop();
}

function startGame() {
  clearInterval(gameInterval); // avoids multiple loops (when user clicks start multiple times)
  gameInterval = setInterval(() => {
    ctx.clearRect(0, 0, 400, 400);
    gameBackground();
    updateSnake();
    drawSnakeAndFood();
  }, 200);
}

function displayGameOver() {
  drawSnakeAndFood();
  ctx.font = "40px serif";
  ctx.strokeStyle = "#1302fcff";
  ctx.strokeText("Game Over", 1 * boxSize, 10 * boxSize);
  ctx.strokeStyle = "black";
}

function collision(isCollision) {
  if (isCollision) {
    clearInterval(gameInterval);
    displayGameOver();
  }
}

function restartGame() {
  clearInterval(gameInterval);
  snakeBody = [{ x: 5, y: 5 }];
  dir = "right";
  spawnFood();
  isCollision = false;
  startGame();
}

startButton.addEventListener("click", () => {
  startButton.innerHTML = "Restart";
  if (isCollision) restartGame();
  else startGame();
});

stopButton.addEventListener("click", () => {
  clearInterval(gameInterval);
});
