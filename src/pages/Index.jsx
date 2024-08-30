import React, { useState, useEffect, useRef } from 'react';
import { Button } from "@/components/ui/button";
import { toast } from 'sonner';
import { motion, AnimatePresence } from 'framer-motion';

const GRID_SIZE = 10;
const SHIP_SIZES = [5, 4, 3, 3, 2];

const Index = () => {
  const [gameState, setGameState] = useState('menu');
  const [playerGrid, setPlayerGrid] = useState(Array(GRID_SIZE).fill().map(() => Array(GRID_SIZE).fill(0)));
  const [opponentGrid, setOpponentGrid] = useState(Array(GRID_SIZE).fill().map(() => Array(GRID_SIZE).fill(0)));
  const [playerShips, setPlayerShips] = useState([]);
  const [opponentShips, setOpponentShips] = useState([]);
  const [currentShipIndex, setCurrentShipIndex] = useState(0);
  const [isPlayerTurn, setIsPlayerTurn] = useState(true);
  const [winner, setWinner] = useState(null);
  const [isVertical, setIsVertical] = useState(false);
  const [backgroundMusic, setBackgroundMusic] = useState(null);
  const [isMusicPlaying, setIsMusicPlaying] = useState(false);
  const canvasRef = useRef(null);

  useEffect(() => {
    if (gameState === 'playing' || gameState === 'placing') {
      const audio = new Audio('/assets/sounds/ocean_ambience.mp3');
      audio.loop = true;
      setBackgroundMusic(audio);
      setIsMusicPlaying(true);
      audio.play();
      return () => {
        audio.pause();
        setBackgroundMusic(null);
      };
    }
  }, [gameState]);

  useEffect(() => {
    if (canvasRef.current) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      let animationFrameId;

      const render = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        // Add ocean wave animation here
        ctx.fillStyle = 'rgba(0, 100, 255, 0.3)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        animationFrameId = requestAnimationFrame(render);
      };

      render();

      return () => {
        cancelAnimationFrame(animationFrameId);
      };
    }
  }, []);

  const handleStartGame = () => {
    setGameState('placing');
    setPlayerGrid(Array(GRID_SIZE).fill().map(() => Array(GRID_SIZE).fill(0)));
    setOpponentGrid(Array(GRID_SIZE).fill().map(() => Array(GRID_SIZE).fill(0)));
    setPlayerShips([]);
    setOpponentShips([]);
    setCurrentShipIndex(0);
    placeOpponentShips();
  };

  const placeOpponentShips = () => {
    const newOpponentGrid = [...opponentGrid];
    const newOpponentShips = [];

    SHIP_SIZES.forEach(size => {
      let placed = false;
      while (!placed) {
        const row = Math.floor(Math.random() * GRID_SIZE);
        const col = Math.floor(Math.random() * GRID_SIZE);
        const isHorizontal = Math.random() < 0.5;

        if (canPlaceShip(newOpponentGrid, row, col, size, isHorizontal)) {
          placeShip(newOpponentGrid, row, col, size, isHorizontal);
          newOpponentShips.push({ row, col, size, isHorizontal });
          placed = true;
        }
      }
    });

    setOpponentGrid(newOpponentGrid);
    setOpponentShips(newOpponentShips);
  };

  const canPlaceShip = (grid, row, col, size, isHorizontal) => {
    if (isHorizontal) {
      if (col + size > GRID_SIZE) return false;
      for (let i = 0; i < size; i++) {
        if (grid[row][col + i] !== 0) return false;
      }
    } else {
      if (row + size > GRID_SIZE) return false;
      for (let i = 0; i < size; i++) {
        if (grid[row + i][col] !== 0) return false;
      }
    }
    return true;
  };

  const placeShip = (grid, row, col, size, isHorizontal) => {
    if (isHorizontal) {
      for (let i = 0; i < size; i++) {
        grid[row][col + i] = 1;
      }
    } else {
      for (let i = 0; i < size; i++) {
        grid[row + i][col] = 1;
      }
    }
  };

  const handlePlayerPlacement = (row, col) => {
    if (currentShipIndex >= SHIP_SIZES.length) return;

    const size = SHIP_SIZES[currentShipIndex];

    if (canPlaceShip(playerGrid, row, col, size, isVertical)) {
      const newPlayerGrid = [...playerGrid];
      placeShip(newPlayerGrid, row, col, size, isVertical);
      setPlayerGrid(newPlayerGrid);
      setPlayerShips([...playerShips, { row, col, size, isHorizontal: !isVertical }]);
      setCurrentShipIndex(currentShipIndex + 1);
      playSound('/assets/sounds/place_ship.wav');

      if (currentShipIndex + 1 >= SHIP_SIZES.length) {
        setGameState('playing');
      }
    } else {
      toast.error("Can't place ship here!");
    }
  };

  const handleAttack = (row, col) => {
    if (!isPlayerTurn || opponentGrid[row][col] === 2 || opponentGrid[row][col] === 3) return;

    const newOpponentGrid = [...opponentGrid];
    if (newOpponentGrid[row][col] === 1) {
      newOpponentGrid[row][col] = 2; // Hit
      playSound('/assets/sounds/hit.wav');
      toast.success("It's a hit!");
      animateMissile(row, col, true);
    } else {
      newOpponentGrid[row][col] = 3; // Miss
      playSound('/assets/sounds/miss.wav');
      toast.info("It's a miss!");
      animateMissile(row, col, false);
    }

    setOpponentGrid(newOpponentGrid);
    setIsPlayerTurn(false);
    setTimeout(opponentTurn, 2000);

    if (checkForWin(newOpponentGrid)) {
      setWinner('Player');
      setGameState('gameOver');
      playSound('/assets/sounds/victory.wav');
    }
  };

  const opponentTurn = () => {
    let row, col;
    do {
      row = Math.floor(Math.random() * GRID_SIZE);
      col = Math.floor(Math.random() * GRID_SIZE);
    } while (playerGrid[row][col] === 2 || playerGrid[row][col] === 3);

    const newPlayerGrid = [...playerGrid];
    if (newPlayerGrid[row][col] === 1) {
      newPlayerGrid[row][col] = 2; // Hit
      playSound('/assets/sounds/hit.wav');
      toast.error("Opponent hit your ship!");
    } else {
      newPlayerGrid[row][col] = 3; // Miss
      playSound('/assets/sounds/miss.wav');
      toast.info("Opponent missed!");
    }

    setPlayerGrid(newPlayerGrid);
    setIsPlayerTurn(true);

    if (checkForWin(newPlayerGrid)) {
      setWinner('Opponent');
      setGameState('gameOver');
      playSound('/assets/sounds/defeat.wav');
    }
  };

  const checkForWin = (grid) => {
    return !grid.some(row => row.includes(1));
  };

  const playSound = (soundPath) => {
    const audio = new Audio(soundPath);
    audio.play();
  };

  const animateMissile = (row, col, isHit) => {
    // Implement missile animation logic here
    console.log(`Missile fired at (${row}, ${col}). Hit: ${isHit}`);
  };

  const toggleMusic = () => {
    if (backgroundMusic) {
      if (isMusicPlaying) {
        backgroundMusic.pause();
      } else {
        backgroundMusic.play();
      }
      setIsMusicPlaying(!isMusicPlaying);
    }
  };

  const renderCell = (cell, i, j, isOpponent) => {
    let cellContent = null;
    let cellClass = 'w-10 h-10 border ';

    if (cell === 0) {
      cellClass += 'bg-blue-200';
    } else if (cell === 1) {
      cellClass += isOpponent ? 'bg-blue-200' : 'bg-gray-500';
      cellContent = <img src="/assets/images/ship.png" alt="Ship" className="w-full h-full object-cover" />;
    } else if (cell === 2) {
      cellClass += 'bg-red-500';
      cellContent = <img src="/assets/images/explosion.png" alt="Hit" className="w-full h-full object-cover" />;
    } else if (cell === 3) {
      cellClass += 'bg-white';
      cellContent = <img src="/assets/images/splash.png" alt="Miss" className="w-full h-full object-cover" />;
    }

    if ((isOpponent && gameState === 'playing') || (!isOpponent && gameState === 'placing')) {
      cellClass += ' cursor-pointer hover:bg-blue-300';
    }

    return (
      <motion.div
        key={`${i}-${j}`}
        className={cellClass}
        onClick={() => {
          if (isOpponent && gameState === 'playing') {
            handleAttack(i, j);
          } else if (!isOpponent && gameState === 'placing') {
            handlePlayerPlacement(i, j);
          }
        }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
      >
        {cellContent}
      </motion.div>
    );
  };

  const renderGrid = (grid, isOpponent) => (
    <div className="grid grid-cols-10 gap-1 mb-4">
      {grid.map((row, i) =>
        row.map((cell, j) => renderCell(cell, i, j, isOpponent))
      )}
    </div>
  );

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-100 relative overflow-hidden">
      <canvas ref={canvasRef} className="absolute inset-0 z-0" width={window.innerWidth} height={window.innerHeight} />
      <div className="z-10 relative">
        {gameState === 'menu' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="flex flex-col items-center"
          >
            <img src="/assets/images/logo.png" alt="Battleship Logo" className="w-64 mb-8" />
            <Button onClick={handleStartGame} className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 text-xl">
              Start Game
            </Button>
          </motion.div>
        )}
        {gameState === 'placing' && (
          <div className="flex flex-col items-center">
            <h2 className="text-2xl mb-4 text-white">Place your ships</h2>
            {renderGrid(playerGrid, false)}
            <p className="text-white">Place ship of size {SHIP_SIZES[currentShipIndex]}</p>
            <Button onClick={() => setIsVertical(!isVertical)} className="mt-4">
              Rotate Ship
            </Button>
          </div>
        )}
        {gameState === 'playing' && (
          <div className="flex flex-col items-center">
            <h2 className="text-2xl mb-4 text-white">{isPlayerTurn ? "Your turn" : "Opponent's turn"}</h2>
            <div className="flex justify-between w-full space-x-8">
              <div>
                <h3 className="text-xl mb-2 text-white">Your Grid</h3>
                {renderGrid(playerGrid, false)}
              </div>
              <div>
                <h3 className="text-xl mb-2 text-white">Opponent's Grid</h3>
                {renderGrid(opponentGrid, true)}
              </div>
            </div>
          </div>
        )}
        {gameState === 'gameOver' && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center bg-white p-8 rounded-lg shadow-lg"
          >
            <h2 className="text-3xl mb-4 font-bold">{winner === 'Player' ? 'Victory!' : 'Defeat'}</h2>
            <p className="text-xl mb-6">{winner === 'Player' ? 'You won the battle!' : 'The enemy has defeated your fleet.'}</p>
            <Button onClick={() => setGameState('menu')} className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 text-xl">
              Back to Menu
            </Button>
          </motion.div>
        )}
      </div>
      <Button onClick={toggleMusic} className="absolute top-4 right-4 z-20">
        {isMusicPlaying ? 'Mute Music' : 'Play Music'}
      </Button>
    </div>
  );
};

export default Index;