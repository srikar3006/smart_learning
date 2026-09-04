/* Smart Learning — Games page engine (self-contained, no backend games API yet).
   Persists progress in localStorage behind a small store so backend sync can be
   added later without touching the game code (see Store.save/load). */
(function () {
  'use strict';

  /* ---------------- constants ---------------- */
  var DIFF_LABEL = ['Very Easy', 'Very Easy', 'Easy', 'Easy', 'Medium', 'Medium', 'Hard', 'Hard', 'Very Hard', 'Expert'];

  var GAME_META = {
    coloring: { name: 'Coloring Fun', icon: '🎨', category: 'Creativity', desc: 'Coloring & painting with fun' },
    puzzle: { name: 'Puzzle Time', icon: '🧩', category: 'Cognitive', desc: 'Jigsaw puzzles to improve thinking' },
    shape: { name: 'Shape Builder', icon: '🔷', category: 'Maths', desc: 'Learn shapes by building & matching' },
    number: { name: 'Number Match', icon: '🔢', category: 'Maths', desc: 'Match numbers and have fun' },
    memory: { name: 'Memory Game', icon: '🧠', category: 'Cognitive', desc: 'Improve memory with matching cards' },
    word: { name: 'Word Builder', icon: '🔤', category: 'Language', desc: 'Make words and learn spellings' },
    difference: { name: 'Spot the Difference', icon: '🔎', category: 'Cognitive', desc: 'Find the differences in pictures' },
    maze: { name: 'Maze Adventure', icon: '🏁', category: 'General', desc: 'Solve mazes and reach the goal' }
  };
  var GAME_ORDER = ['coloring', 'puzzle', 'shape', 'number', 'memory', 'word', 'difference', 'maze'];

  var ACHIEVEMENTS = [
    { id: 'first_game', icon: '🎮', name: 'First Game', desc: 'Play any game', test: function (s) { return s.stats.gamesPlayed >= 1; } },
    { id: 'five_levels', icon: '🥉', name: '5 Levels Completed', desc: 'Complete 5 levels', test: function (s) { return s.stats.levelsCompleted >= 5; } },
    { id: 'ten_levels', icon: '🥈', name: '10 Levels Completed', desc: 'Complete 10 levels', test: function (s) { return s.stats.levelsCompleted >= 10; } },
    { id: 'puzzle_master', icon: '🧩', name: 'Puzzle Master', desc: 'Finish all Puzzle Time levels', test: function (s) { return gameDone(s, 'puzzle'); } },
    { id: 'memory_master', icon: '🧠', name: 'Memory Master', desc: 'Finish all Memory Game levels', test: function (s) { return gameDone(s, 'memory'); } },
    { id: 'maths_star', icon: '🔢', name: 'Maths Star', desc: 'Finish all Number Match levels', test: function (s) { return gameDone(s, 'number'); } },
    { id: 'word_builder', icon: '🔤', name: 'Word Builder', desc: 'Finish all Word Builder levels', test: function (s) { return gameDone(s, 'word'); } },
    { id: 'game_explorer', icon: '🗺️', name: 'Game Explorer', desc: 'Play every game once', test: function (s) { return GAME_ORDER.every(function (k) { return s.games[k] && s.games[k].plays > 0; }); } }
  ];
  function gameDone(s, key) { return s.games[key] && s.games[key].completedLevels.length >= 10; }

  /* ---------------- store ---------------- */
  var STORE_KEY = 'sl_games_state_v2';
  function freshState() {
    var games = {};
    GAME_ORDER.forEach(function (k) {
      games[k] = { unlockedLevel: 1, completedLevels: [], bestScore: 0, totalScore: 0, lastLevel: 1, plays: 0 };
    });
    return { games: games, lastPlayed: null, history: [], myList: [], achievements: {}, stats: { gamesPlayed: 0, levelsCompleted: 0 } };
  }
  var Store = {
    state: null,
    load: function () {
      if (this.state) return this.state;
      try {
        var raw = localStorage.getItem(STORE_KEY);
        var parsed = raw ? JSON.parse(raw) : null;
        this.state = parsed && parsed.games ? parsed : freshState();
      } catch (e) { this.state = freshState(); }
      GAME_ORDER.forEach(function (k) { if (!this.state.games[k]) this.state.games[k] = freshState().games[k]; }, this);
      return this.state;
    },
    save: function () {
      try { localStorage.setItem(STORE_KEY, JSON.stringify(this.state)); } catch (e) { /* storage unavailable */ }
    }
  };

  function checkAchievements() {
    var s = Store.load();
    var unlocked = [];
    ACHIEVEMENTS.forEach(function (a) {
      if (!s.achievements[a.id] && a.test(s)) {
        s.achievements[a.id] = Date.now();
        unlocked.push(a);
      }
    });
    if (unlocked.length) Store.save();
    return unlocked;
  }

  /* ---------------- small helpers ---------------- */
  function rand(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
  function shuffle(arr) { var a = arr.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
  function pad2(n) { return n < 10 ? '0' + n : '' + n; }
  function fmtTime(sec) { sec = Math.max(0, Math.round(sec)); return pad2(Math.floor(sec / 60)) + ':' + pad2(sec % 60); }
  function el(tag, cls, html) { var d = document.createElement(tag); if (cls) d.className = cls; if (html !== undefined) d.innerHTML = html; return d; }

  /* ================================================================
     GAME MODULES
     Each render(area, level, api) fully renders the level in `area`.
     api.complete(score, meta) -> tells controller the level is finished.
     api.onCleanup(fn) -> register teardown (timers / listeners).
     api.setMsg(text) -> optional status line.
     ================================================================ */
  var Games = {};

  /* ---------- 1. Coloring Fun ---------- */
  Games.coloring = function (area, level, api) {
    var petals = Math.min(4 + level, 13);
    var hasLeaves = level >= 5;
    var hasGround = level >= 8;
    area.innerHTML =
      '<canvas class="gp-color-canvas" width="820" height="360"></canvas>' +
      '<div class="gp-palette" id="pal"></div>' +
      '<div class="gp-actions">' +
      '<button class="gp-btn secondary" id="undo">↺ Undo</button>' +
      '<button class="gp-btn secondary" id="clear">Clear</button>' +
      '</div><div class="gp-msg" id="msg">Colored 0%</div>';
    var c = area.querySelector('canvas'), ctx = c.getContext('2d');
    var pal = area.querySelector('#pal'), msg = area.querySelector('#msg');
    var colors = ['#ef476f', '#ff9f1c', '#ffd166', '#06d6a0', '#118ab2', '#7b61ff', '#f78fb3', '#7a4a1f', '#333333'];
    var color = colors[0], mode = 'fill';

    // build regions
    var regions = [];
    var cx = 410, cy = 170, r = 46;
    regions.push({ path: circlePath(cx, cy, r), fill: null }); // center
    for (var i = 0; i < petals; i++) {
      var ang = (Math.PI * 2 * i) / petals;
      var px = cx + Math.cos(ang) * (r + 34);
      var py = cy + Math.sin(ang) * (r + 34);
      regions.push({ path: circlePath(px, py, 26), fill: null });
    }
    if (hasLeaves) {
      regions.push({ path: leafPath(cx - 60, cy + 130), fill: null });
      regions.push({ path: leafPath(cx + 60, cy + 130), fill: null });
    }
    regions.push({ path: stemPath(cx, cy + r, cx, cy + 150 + (hasLeaves ? 20 : 0)), fill: null });
    if (hasGround) regions.push({ path: rectPath(20, 330, 780, 20), fill: null });

    function circlePath(x, y, rad) { var p = new Path2D(); p.arc(x, y, rad, 0, Math.PI * 2); return p; }
    function leafPath(x, y) { var p = new Path2D(); p.ellipse(x, y, 26, 14, Math.PI / 4, 0, Math.PI * 2); return p; }
    function stemPath(x1, y1, x2, y2) { var p = new Path2D(); p.rect(x1 - 5, y1, 10, y2 - y1); return p; }
    function rectPath(x, y, w, h) { var p = new Path2D(); p.rect(x, y, w, h); return p; }

    var undoStack = [];
    function paint() {
      ctx.fillStyle = '#fffdf7'; ctx.fillRect(0, 0, c.width, c.height);
      regions.forEach(function (rg) {
        ctx.fillStyle = rg.fill || '#ffffff';
        ctx.fill(rg.path);
        ctx.lineWidth = 3; ctx.strokeStyle = '#9b91bb'; ctx.stroke(rg.path);
      });
      var done = regions.filter(function (r) { return r.fill; }).length;
      var pct = Math.round((done / regions.length) * 100);
      msg.textContent = 'Colored ' + pct + '%';
      if (pct >= 100) {
        api.complete(Math.max(60, 100 - undoStack.length * 3), {});
      }
    }
    colors.forEach(function (col) {
      var s = el('button', 'gp-swatch'); s.style.background = col;
      s.onclick = function () { color = col; mode = 'fill'; area.querySelectorAll('.gp-swatch').forEach(function (x) { x.classList.remove('active'); }); s.classList.add('active'); };
      pal.appendChild(s);
    });
    var eraser = el('button', 'gp-swatch erase');
    eraser.onclick = function () { mode = 'erase'; area.querySelectorAll('.gp-swatch').forEach(function (x) { x.classList.remove('active'); }); eraser.classList.add('active'); };
    pal.appendChild(eraser);

    function pointerPos(e) {
      var r0 = c.getBoundingClientRect();
      return { x: (e.clientX - r0.left) * (c.width / r0.width), y: (e.clientY - r0.top) * (c.height / r0.height) };
    }
    function onDown(e) {
      e.preventDefault();
      var p = pointerPos(e);
      for (var i = regions.length - 1; i >= 0; i--) {
        if (ctx.isPointInPath(regions[i].path, p.x, p.y)) {
          var before = regions[i].fill;
          var after = mode === 'erase' ? null : color;
          if (before !== after) { undoStack.push({ region: regions[i], prev: before }); regions[i].fill = after; paint(); }
          break;
        }
      }
    }
    c.addEventListener('pointerdown', onDown);
    area.querySelector('#undo').onclick = function () {
      var last = undoStack.pop();
      if (last) { last.region.fill = last.prev; paint(); }
    };
    area.querySelector('#clear').onclick = function () { regions.forEach(function (r) { r.fill = null; }); undoStack = []; paint(); };
    api.onCleanup(function () { c.removeEventListener('pointerdown', onDown); });
    paint();
  };

  /* ---------- 2. Puzzle Time (real jigsaw, drag + snap) ---------- */
  Games.puzzle = function (area, level, api) {
    var dims = [[2, 2], [2, 2], [2, 3], [3, 2], [3, 3], [3, 3], [4, 3], [3, 4], [4, 4], [5, 4]][level - 1];
    var cols = dims[0], rows = dims[1];
    var total = cols * rows;
    var boardMax = 380, pieceSize = Math.floor(Math.min(boardMax / cols, 300 / rows));
    var hue = (level * 41) % 360;
    var bg = 'conic-gradient(from ' + hue + 'deg, hsl(' + hue + ',80%,65%), hsl(' + ((hue + 90) % 360) + ',80%,60%), hsl(' + ((hue + 200) % 360) + ',80%,55%), hsl(' + hue + ',80%,65%))';
    var bgSize = (cols * pieceSize) + 'px ' + (rows * pieceSize) + 'px';

    area.innerHTML =
      '<div class="gp-jig-wrap">' +
      '<div class="gp-jig-slots" id="slots" style="grid-template-columns:repeat(' + cols + ',' + pieceSize + 'px)"></div>' +
      '<div class="gp-jig-tray" id="tray"></div>' +
      '</div><div class="gp-msg">Placed <span id="placedCount">0</span> / ' + total + ' · <span id="timer">00:00</span></div>';

    var slotsEl = area.querySelector('#slots'), tray = area.querySelector('#tray'), placedCountEl = area.querySelector('#placedCount'), timerEl = area.querySelector('#timer');
    var slots = [], placed = 0, moves = 0;
    for (var i = 0; i < total; i++) {
      var slot = el('div', 'gp-jig-slot');
      slot.style.width = pieceSize + 'px'; slot.style.height = pieceSize + 'px';
      slot.dataset.index = i;
      slotsEl.appendChild(slot);
      slots.push(slot);
    }
    var order = shuffle(Array.from({ length: total }, function (_, i) { return i; }));
    var pieces = order.map(function (correctIndex) {
      var p = el('div', 'gp-jig-piece');
      p.style.width = pieceSize + 'px'; p.style.height = pieceSize + 'px';
      p.style.backgroundImage = bg; p.style.backgroundSize = bgSize;
      var r = Math.floor(correctIndex / cols), cN = correctIndex % cols;
      p.style.backgroundPosition = (-cN * pieceSize) + 'px ' + (-r * pieceSize) + 'px';
      p.dataset.correct = correctIndex;
      tray.appendChild(p);
      return p;
    });

    var start = Date.now(), timerId = setInterval(function () { timerEl.textContent = fmtTime((Date.now() - start) / 1000); }, 1000);
    api.onCleanup(function () { clearInterval(timerId); });

    var dragging = null, offX = 0, offY = 0;
    function down(e) {
      var piece = e.target.closest('.gp-jig-piece');
      if (!piece || piece.classList.contains('locked')) return;
      e.preventDefault();
      var rect = piece.getBoundingClientRect();
      dragging = piece; offX = e.clientX - rect.left; offY = e.clientY - rect.top;
      piece.classList.add('dragging');
      piece.style.left = rect.left + 'px'; piece.style.top = rect.top + 'px';
      document.body.appendChild(piece);
      move(e);
    }
    function move(e) {
      if (!dragging) return;
      dragging.style.left = (e.clientX - offX) + 'px';
      dragging.style.top = (e.clientY - offY) + 'px';
    }
    function up(e) {
      if (!dragging) return;
      var piece = dragging; dragging = null; piece.classList.remove('dragging');
      var target = null, best = 1e9;
      slots.forEach(function (s) {
        if (s.classList.contains('filled')) return;
        var r = s.getBoundingClientRect();
        var dx = (r.left + r.width / 2) - e.clientX, dy = (r.top + r.height / 2) - e.clientY;
        var d = dx * dx + dy * dy;
        if (d < best && d < (pieceSize * pieceSize)) { best = d; target = s; }
      });
      moves++;
      if (target && Number(target.dataset.index) === Number(piece.dataset.correct)) {
        target.appendChild(piece);
        piece.style.position = 'static'; piece.style.left = ''; piece.style.top = '';
        target.classList.add('filled');
        placed++;
        placedCountEl.textContent = placed;
        if (placed >= total) {
          clearInterval(timerId);
          var secs = (Date.now() - start) / 1000;
          var score = Math.max(50, 100 - Math.round(secs / 4) - Math.max(0, moves - total) * 2);
          api.complete(score, {});
        }
      } else {
        tray.appendChild(piece);
        piece.style.position = 'static'; piece.style.left = ''; piece.style.top = '';
      }
    }
    area.addEventListener('pointerdown', down);
    window.addEventListener('pointermove', move);
    window.addEventListener('pointerup', up);
    api.onCleanup(function () {
      area.removeEventListener('pointerdown', down);
      window.removeEventListener('pointermove', move);
      window.removeEventListener('pointerup', up);
    });
    pieces.forEach(function (p) { p.style.touchAction = 'none'; });
  };

  /* ---------- 3. Shape Builder ---------- */
  Games.shape = function (area, level, api) {
    var pool = ['●', '▲', '■', '★', '◆', '⬟', '⬢', '✚'];
    var count = Math.min(3 + Math.floor((level - 1) / 1.3), 8);
    var shapes = pool.slice(0, count);
    var distractors = level >= 5 ? Math.min(Math.floor(level / 4), 3) : 0;
    var rotate = level >= 6;

    area.innerHTML =
      '<div class="gp-shape-board">' +
      '<div class="gp-shape-col"><b>Targets</b><div class="gp-shape-grid" id="targets"></div></div>' +
      '<div class="gp-shape-col"><b>Shapes</b><div class="gp-shape-grid" id="pieces"></div></div>' +
      '</div><div class="gp-msg" id="msg">Matched 0 / ' + shapes.length + '</div>';
    var t = area.querySelector('#targets'), p = area.querySelector('#pieces'), msg = area.querySelector('#msg');
    var matched = 0, attempts = 0;
    shapes.forEach(function (s) {
      var box = el('div', 'gp-shape-box', '?');
      box.dataset.shape = s;
      box.style.transform = rotate ? 'rotate(' + rand(-25, 25) + 'deg)' : '';
      box.onclick = function () { tryMatch(box); };
      t.appendChild(box);
    });
    var pieceEls = shuffle(shapes.concat(shuffle(pool.filter(function (x) { return shapes.indexOf(x) === -1; })).slice(0, distractors)));
    var selected = null;
    pieceEls.forEach(function (s) {
      var piece = el('div', 'gp-shape-box piece', s);
      piece.dataset.shape = s;
      piece.onclick = function () {
        if (piece.classList.contains('used')) return;
        area.querySelectorAll('.piece').forEach(function (x) { x.style.outline = ''; });
        selected = piece; piece.style.outline = '3px solid #6e2be9';
      };
      p.appendChild(piece);
    });
    function tryMatch(target) {
      if (!selected || target.classList.contains('matched')) return;
      attempts++;
      if (target.dataset.shape === selected.dataset.shape) {
        target.textContent = selected.dataset.shape; target.classList.add('matched'); target.style.transform = '';
        selected.classList.add('used');
        matched++;
        msg.textContent = 'Matched ' + matched + ' / ' + shapes.length;
        selected = null;
        if (matched >= shapes.length) {
          var score = Math.max(50, 100 - Math.max(0, attempts - shapes.length) * 5);
          api.complete(score, {});
        }
      } else {
        msg.textContent = 'Not quite — try another shape!';
      }
    }
  };

  /* ---------- 4. Number Match ---------- */
  function numberQuestion(level) {
    var op, a, b, ans, prompt, choicesPool;
    function starsFor(n) { return '⭐'.repeat(n); }
    if (level <= 2) {
      a = rand(1, level === 1 ? 5 : 10); ans = a; prompt = starsFor(a);
      choicesPool = level === 1 ? [1, 2, 3, 4, 5] : [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    } else if (level === 3) {
      a = rand(1, 20); ans = a; prompt = 'How many? ' + starsFor(Math.min(a, 20)).slice(0, a);
      choicesPool = shuffle(Array.from({ length: 20 }, function (_, i) { return i + 1; }));
    } else if (level === 4) {
      a = rand(1, 6); b = rand(1, 4); ans = a + b; prompt = a + ' + ' + b + ' = ?';
      choicesPool = range(0, 10);
    } else if (level === 5) {
      op = Math.random() < 0.5 ? '+' : '-';
      a = rand(5, 15); b = rand(1, a);
      ans = op === '+' ? a + b : a - b; prompt = a + ' ' + op + ' ' + b + ' = ?';
      choicesPool = range(0, 20);
    } else if (level === 6) {
      op = Math.random() < 0.5 ? '+' : '-';
      a = rand(20, 50); b = rand(10, a);
      ans = op === '+' ? a + b : a - b; prompt = a + ' ' + op + ' ' + b + ' = ?';
      choicesPool = range(Math.max(0, ans - 20), ans + 20);
    } else if (level === 7) {
      a = rand(2, 5); b = rand(2, 5); ans = a * b; prompt = a + ' × ' + b + ' = ?';
      choicesPool = range(1, 25);
    } else if (level === 8) {
      b = rand(2, 5); ans = rand(2, 8); a = b * ans; prompt = a + ' ÷ ' + b + ' = ?';
      choicesPool = range(1, 10);
    } else {
      var ops = ['+', '-', '×', '÷'];
      op = ops[rand(0, 3)];
      if (op === '+') { a = rand(5, 30); b = rand(5, 30); ans = a + b; }
      else if (op === '-') { a = rand(10, 40); b = rand(1, a); ans = a - b; }
      else if (op === '×') { a = rand(2, 9); b = rand(2, 9); ans = a * b; }
      else { b = rand(2, 9); ans = rand(2, 9); a = b * ans; }
      prompt = a + ' ' + op + ' ' + b + ' = ?';
      choicesPool = range(Math.max(0, ans - 15), ans + 15);
    }
    var choices = shuffle(Array.from(new Set(shuffle(choicesPool).filter(function (x) { return x !== ans; }).slice(0, 5).concat([ans]))));
    return { prompt: prompt, answer: ans, choices: choices };
    function range(min, max) { var arr = []; for (var i = min; i <= max; i++) arr.push(i); return arr; }
  }
  Games.number = function (area, level, api) {
    var timed = level === 10;
    var roundsTotal = timed ? 6 : 5;
    var round = 0, correct = 0, timeLeft = 30, timerId = null;
    area.innerHTML =
      (timed ? '<div class="gp-timer" id="tt">⏱ 30s</div>' : '') +
      '<div class="gp-number-question" id="q"></div>' +
      '<div class="gp-number-grid" id="choices"></div>' +
      '<div class="gp-msg" id="msg">Question 1 / ' + roundsTotal + '</div>';
    var qEl = area.querySelector('#q'), cEl = area.querySelector('#choices'), msg = area.querySelector('#msg'), ttEl = area.querySelector('#tt');
    var current;
    function newRound() {
      current = numberQuestion(level);
      qEl.textContent = current.prompt;
      cEl.innerHTML = '';
      current.choices.forEach(function (c) {
        var b = el('button', 'gp-number-choice', c);
        b.onclick = function () { answer(b, c); };
        cEl.appendChild(b);
      });
      msg.textContent = 'Question ' + (round + 1) + ' / ' + roundsTotal;
    }
    function answer(btn, val) {
      if (btn.classList.contains('correct') || btn.classList.contains('wrong')) return;
      var isRight = val === current.answer;
      btn.classList.add(isRight ? 'correct' : 'wrong');
      if (isRight) correct++;
      else {
        Array.prototype.forEach.call(cEl.children, function (c) { if (Number(c.textContent) === current.answer) c.classList.add('correct'); });
      }
      round++;
      setTimeout(function () {
        if (round >= roundsTotal) finish();
        else newRound();
      }, 500);
    }
    function finish() {
      if (timerId) clearInterval(timerId);
      var score = Math.round((correct / roundsTotal) * 100);
      if (correct / roundsTotal >= 0.6) api.complete(Math.max(score, 60), {});
      else { msg.textContent = '🙂 Score ' + score + '% — try again to pass 60%!'; round = 0; correct = 0; setTimeout(newRound, 900); }
    }
    if (timed) {
      timerId = setInterval(function () {
        timeLeft--; ttEl.textContent = '⏱ ' + timeLeft + 's';
        if (timeLeft <= 0) finish();
      }, 1000);
      api.onCleanup(function () { clearInterval(timerId); });
    }
    newRound();
  };

  /* ---------- 5. Memory Game ---------- */
  Games.memory = function (area, level, api) {
    var pairsTable = [2, 3, 4, 5, 6, 8, 10, 12, 15, 18];
    var pairs = pairsTable[level - 1];
    var icons = ['🐘', '🐱', '🐶', '🦁', '🐸', '🦄', '🐵', '🐼', '🐨', '🦊', '🐷', '🐰', '🐯', '🦋', '🐙', '🐢', '🦉', '🐳'];
    var vals = shuffle(icons.slice(0, pairs).concat(icons.slice(0, pairs)));
    var cols = Math.min(Math.ceil(Math.sqrt(vals.length * 1.6)), 8);
    area.innerHTML = '<div class="gp-memory-grid" id="grid" style="grid-template-columns:repeat(' + cols + ',1fr)"></div><div class="gp-msg" id="msg">Pairs 0 / ' + pairs + ' · Moves 0</div>';
    var grid = area.querySelector('#grid'), msg = area.querySelector('#msg');
    var openCards = [], lock = false, found = 0, moves = 0;
    vals.forEach(function (v) {
      var card = el('button', 'gp-memory-card', v);
      card.dataset.v = v; card.textContent = '';
      card.onclick = function () { flip(card); };
      grid.appendChild(card);
    });
    function flip(card) {
      if (lock || card.classList.contains('open') || card.classList.contains('matched')) return;
      card.classList.add('open'); card.textContent = card.dataset.v;
      openCards.push(card);
      if (openCards.length === 2) {
        lock = true; moves++;
        if (openCards[0].dataset.v === openCards[1].dataset.v) {
          openCards.forEach(function (c) { c.classList.add('matched'); c.classList.remove('open'); });
          found++; openCards = []; lock = false;
          msg.textContent = 'Pairs ' + found + ' / ' + pairs + ' · Moves ' + moves;
          if (found >= pairs) {
            var score = Math.max(50, 100 - Math.max(0, moves - pairs) * 2);
            api.complete(score, {});
          }
        } else {
          setTimeout(function () {
            openCards.forEach(function (c) { c.classList.remove('open'); c.textContent = ''; });
            openCards = []; lock = false;
            msg.textContent = 'Pairs ' + found + ' / ' + pairs + ' · Moves ' + moves;
          }, 700);
        }
      }
    }
  };

  /* ---------- 6. Word Builder ---------- */
  var WORD_BANK = [
    [['🐱', 'CAT'], ['🐶', 'DOG'], ['☀️', 'SUN']],
    [['🚌', 'BUS'], ['🖊️', 'PEN'], ['🎩', 'HAT']],
    [['🦁', 'LION'], ['🐦', 'BIRD'], ['📖', 'BOOK']],
    [['🍎', 'APPLE'], ['🐯', 'TIGER'], ['🏠', 'HOUSE']],
    [['🐭', 'MOUSE'], ['✈️', 'PLANE'], ['☁️', 'CLOUD']],
    [['🐰', 'RABBIT'], ['🌸', 'FLOWER'], ['🍊', 'ORANGE']],
    [['🎸', 'GUITAR'], ['🐬', 'DOLPHIN'], ['🚀', 'ROCKET']],
    [['🐘', 'ELEPHANT'], ['🦋', 'BUTTERFLY'], ['🦖', 'DINOSAUR']],
    [['🎵', 'RHYTHM'], ['🛡️', 'KNIGHT'], ['🔬', 'SCIENCE']],
    [['🌟', 'BEAUTIFUL'], ['🗺️', 'ADVENTURE'], ['📚', 'KNOWLEDGE']]
  ];
  Games.word = function (area, level, api) {
    var words = WORD_BANK[level - 1];
    var idx = 0, solved = 0, hints = 0;
    area.innerHTML =
      '<div class="gp-word-pic" id="pic"></div>' +
      '<div class="gp-word-answer" id="ans"></div>' +
      '<div class="gp-word-letters" id="letters"></div>' +
      '<div class="gp-actions"><button class="gp-btn secondary" id="hint">💡 Hint</button><button class="gp-btn secondary" id="back">⌫ Remove</button></div>' +
      '<div class="gp-msg" id="msg">Word 1 / ' + words.length + '</div>';
    var pic = area.querySelector('#pic'), ans = area.querySelector('#ans'), letters = area.querySelector('#letters'), msg = area.querySelector('#msg');
    var word, slots, placedIdx;
    function load() {
      word = words[idx][1]; pic.textContent = words[idx][0];
      placedIdx = [];
      ans.innerHTML = ''; slots = [];
      for (var i = 0; i < word.length; i++) { var s = el('div', 'gp-word-slot', ''); ans.appendChild(s); slots.push(s); }
      letters.innerHTML = '';
      shuffle(word.split('')).forEach(function (ch, i) {
        var b = el('button', 'gp-letter', ch);
        b.onclick = function () { place(b, ch); };
        letters.appendChild(b);
      });
      msg.textContent = 'Word ' + (idx + 1) + ' / ' + words.length;
    }
    function place(btn, ch) {
      if (btn.classList.contains('used')) return;
      var next = placedIdx.length;
      if (next >= word.length) return;
      slots[next].textContent = ch;
      btn.classList.add('used');
      placedIdx.push(btn);
      if (next + 1 === word.length) checkWord();
    }
    function checkWord() {
      var built = slots.map(function (s) { return s.textContent; }).join('');
      if (built === word) {
        msg.textContent = '🎉 Correct — ' + word + '!';
        solved++;
        setTimeout(function () {
          idx++;
          if (idx >= words.length) {
            var score = Math.max(50, 100 - hints * 10);
            api.complete(score, {});
          } else load();
        }, 700);
      } else {
        msg.textContent = 'Not quite — try again!';
        setTimeout(function () { placedIdx.forEach(function (b) { b.classList.remove('used'); }); placedIdx = []; slots.forEach(function (s) { s.textContent = ''; }); }, 600);
      }
    }
    area.querySelector('#hint').onclick = function () {
      var next = placedIdx.length;
      if (next >= word.length) return;
      var need = word[next];
      var btn = Array.prototype.find.call(letters.children, function (b) { return !b.classList.contains('used') && b.textContent === need; });
      if (btn) { hints++; place(btn, need); }
    };
    area.querySelector('#back').onclick = function () {
      var last = placedIdx.pop();
      if (last) { last.classList.remove('used'); slots[placedIdx.length].textContent = ''; }
    };
    load();
  };

  /* ---------- 7. Spot the Difference ---------- */
  Games.difference = function (area, level, api) {
    var shapeTypes = ['circle', 'rect', 'triangle', 'star'];
    var palette = ['#ef476f', '#ff9f1c', '#ffd166', '#06d6a0', '#118ab2', '#7b61ff', '#f78fb3'];
    var count = Math.min(6 + level, 16);
    var diffCount = Math.min(1 + Math.floor(level / 1.3), 8);
    var cols = Math.ceil(Math.sqrt(count));
    var cell = 60, pad = 10, w = cols * cell + pad * 2, h = Math.ceil(count / cols) * cell + pad * 2;

    var scene = [];
    for (var i = 0; i < count; i++) {
      scene.push({ type: shapeTypes[rand(0, 3)], color: palette[rand(0, palette.length - 1)], scale: 1, visible: true });
    }
    var sceneB = JSON.parse(JSON.stringify(scene));
    var diffIdx = shuffle(Array.from({ length: count }, function (_, i) { return i; })).slice(0, diffCount);
    diffIdx.forEach(function (i) {
      var kind = rand(0, 2);
      if (kind === 0) { var others = palette.filter(function (c) { return c !== sceneB[i].color; }); sceneB[i].color = others[rand(0, others.length - 1)]; }
      else if (kind === 1) { sceneB[i].scale = sceneB[i].scale > 1 ? 0.6 : 1.35; }
      else { sceneB[i].visible = !sceneB[i].visible; }
    });
    var foundSet = {};

    area.innerHTML =
      '<div class="gp-diff-wrap"><svg class="gp-diff-svg" id="a" width="' + w + '" height="' + h + '"></svg><svg class="gp-diff-svg" id="b" width="' + w + '" height="' + h + '"></svg></div>' +
      '<div class="gp-msg" id="msg">Found 0 / ' + diffCount + '</div>';
    var svgA = area.querySelector('#a'), svgB = area.querySelector('#b'), msg = area.querySelector('#msg');

    function drawShape(svg, data, i, isDiffTarget) {
      var r = Math.floor(i / cols), c = i % cols;
      var cx = pad + c * cell + cell / 2, cy = pad + r * cell + cell / 2;
      var s = (cell / 2 - 8) * data.scale;
      var ns = 'http://www.w3.org/2000/svg';
      var g = document.createElementNS(ns, 'g');
      g.setAttribute('data-i', i);
      g.style.cursor = 'pointer';
      if (data.visible) {
        var node;
        if (data.type === 'circle') { node = document.createElementNS(ns, 'circle'); node.setAttribute('cx', cx); node.setAttribute('cy', cy); node.setAttribute('r', s); }
        else if (data.type === 'rect') { node = document.createElementNS(ns, 'rect'); node.setAttribute('x', cx - s); node.setAttribute('y', cy - s); node.setAttribute('width', s * 2); node.setAttribute('height', s * 2); node.setAttribute('rx', 6); }
        else if (data.type === 'triangle') { node = document.createElementNS(ns, 'polygon'); node.setAttribute('points', (cx) + ',' + (cy - s) + ' ' + (cx - s) + ',' + (cy + s) + ' ' + (cx + s) + ',' + (cy + s)); }
        else { node = document.createElementNS(ns, 'polygon'); node.setAttribute('points', starPoints(cx, cy, s)); }
        node.setAttribute('fill', data.color);
        g.appendChild(node);
      }
      svg.appendChild(g);
      g.addEventListener('click', function () { onClickShape(i); });
    }
    function starPoints(cx, cy, s) {
      var pts = [];
      for (var k = 0; k < 10; k++) {
        var ang = (Math.PI / 5) * k - Math.PI / 2;
        var rad = k % 2 === 0 ? s : s * 0.45;
        pts.push((cx + Math.cos(ang) * rad) + ',' + (cy + Math.sin(ang) * rad));
      }
      return pts.join(' ');
    }
    function render() {
      svgA.innerHTML = ''; svgB.innerHTML = '';
      scene.forEach(function (d, i) { drawShape(svgA, d, i); });
      sceneB.forEach(function (d, i) { drawShape(svgB, d, i); });
    }
    function onClickShape(i) {
      if (diffIdx.indexOf(i) === -1) { msg.textContent = 'Not a difference — keep looking!'; return; }
      if (foundSet[i]) return;
      foundSet[i] = true;
      [svgA, svgB].forEach(function (svg) {
        var g = svg.querySelector('g[data-i="' + i + '"]');
        var ring = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        var r = Math.floor(i / cols), c = i % cols;
        ring.setAttribute('cx', pad + c * cell + cell / 2); ring.setAttribute('cy', pad + r * cell + cell / 2);
        ring.setAttribute('r', cell / 2 - 4); ring.setAttribute('fill', 'none'); ring.setAttribute('stroke', '#2ecc71'); ring.setAttribute('stroke-width', '3');
        svg.appendChild(ring);
      });
      var n = Object.keys(foundSet).length;
      msg.textContent = 'Found ' + n + ' / ' + diffCount;
      if (n >= diffCount) {
        var secs = (Date.now() - startTs) / 1000;
        var score = Math.max(50, 100 - Math.round(secs / 3));
        api.complete(score, {});
      }
    }
    var startTs = Date.now();
    render();
  };

  /* ---------- 8. Maze Adventure ---------- */
  function generateMaze(size) {
    var cells = [];
    for (var r = 0; r < size; r++) { var row = []; for (var c = 0; c < size; c++) row.push({ N: true, S: true, E: true, W: true, visited: false }); cells.push(row); }
    var stack = [[0, 0]];
    cells[0][0].visited = true;
    while (stack.length) {
      var cur = stack[stack.length - 1];
      var r = cur[0], c = cur[1];
      var neighbors = [];
      if (r > 0 && !cells[r - 1][c].visited) neighbors.push(['N', r - 1, c]);
      if (r < size - 1 && !cells[r + 1][c].visited) neighbors.push(['S', r + 1, c]);
      if (c > 0 && !cells[r][c - 1].visited) neighbors.push(['W', r, c - 1]);
      if (c < size - 1 && !cells[r][c + 1].visited) neighbors.push(['E', r, c + 1]);
      if (!neighbors.length) { stack.pop(); continue; }
      var pick = neighbors[rand(0, neighbors.length - 1)];
      var dir = pick[0], nr = pick[1], nc = pick[2];
      var opp = { N: 'S', S: 'N', E: 'W', W: 'E' };
      cells[r][c][dir] = false; cells[nr][nc][opp[dir]] = false;
      cells[nr][nc].visited = true;
      stack.push([nr, nc]);
    }
    return cells;
  }
  Games.maze = function (area, level, api) {
    var size = Math.min(5 + level, 15);
    var maze = generateMaze(size);
    var timeLimit = level >= 7 ? 30 + (10 - level) * 5 + 40 : 0;
    var boardPx = Math.min(420, window.innerWidth < 760 ? window.innerWidth - 90 : 420);
    var cellPx = Math.floor(boardPx / size);
    var pos = { r: 0, c: 0 };
    area.innerHTML =
      '<div class="gp-maze-wrap">' +
      (timeLimit ? '<div class="gp-timer" id="tt">⏱ ' + timeLimit + 's</div>' : '') +
      '<div class="gp-maze" id="mz" style="grid-template-columns:repeat(' + size + ',' + cellPx + 'px)"></div>' +
      '<div class="gp-maze-controls"><button class="u">▲</button><button class="l">◀</button><button class="d">▼</button><button class="r">▶</button></div>' +
      '<div class="gp-msg" id="msg">Reach the ⭐ goal!</div></div>';
    var mz = area.querySelector('#mz'), msg = area.querySelector('#msg'), ttEl = area.querySelector('#tt');
    var cellEls = [];
    for (var r = 0; r < size; r++) {
      cellEls.push([]);
      for (var c = 0; c < size; c++) {
        var cellD = maze[r][c];
        var d = el('div', 'gp-maze-cell');
        d.style.width = cellPx + 'px'; d.style.height = cellPx + 'px';
        d.style.borderTop = cellD.N ? '2px solid #5f4ba4' : '2px solid transparent';
        d.style.borderLeft = cellD.W ? '2px solid #5f4ba4' : '2px solid transparent';
        d.style.borderRight = cellD.E ? '2px solid #5f4ba4' : '2px solid transparent';
        d.style.borderBottom = cellD.S ? '2px solid #5f4ba4' : '2px solid transparent';
        mz.appendChild(d);
        cellEls[r].push(d);
      }
    }
    function draw() {
      cellEls.forEach(function (row, r) { row.forEach(function (cellDiv, c) {
        cellDiv.className = 'gp-maze-cell' + (r === 0 && c === 0 ? ' start' : '') + (r === size - 1 && c === size - 1 ? ' goal' : '');
        cellDiv.textContent = (pos.r === r && pos.c === c) ? '🧒' : (r === size - 1 && c === size - 1 ? '⭐' : '');
      }); });
    }
    function move(dr, dc) {
      var cellD = maze[pos.r][pos.c];
      if (dr === -1 && cellD.N) return; if (dr === 1 && cellD.S) return;
      if (dc === -1 && cellD.W) return; if (dc === 1 && cellD.E) return;
      pos.r += dr; pos.c += dc; draw();
      if (pos.r === size - 1 && pos.c === size - 1) {
        if (timerId) clearInterval(timerId);
        var score = timeLimit ? Math.max(60, 100 - Math.round(((timeLimit - timeLeft) / timeLimit) * 40)) : 100;
        api.complete(score, {});
      }
    }
    var timerId = null, timeLeft = timeLimit;
    function tick() {
      timeLeft--; ttEl.textContent = '⏱ ' + timeLeft + 's';
      if (timeLeft <= 0) {
        msg.textContent = "⏰ Time's up — try again!";
        pos = { r: 0, c: 0 }; timeLeft = timeLimit; ttEl.textContent = '⏱ ' + timeLeft + 's'; draw();
      }
    }
    if (timeLimit) {
      timerId = setInterval(tick, 1000);
      api.onCleanup(function () { clearInterval(timerId); });
    }
    var keyHandler = function (e) {
      var map = { ArrowUp: [-1, 0], ArrowDown: [1, 0], ArrowLeft: [0, -1], ArrowRight: [0, 1], w: [-1, 0], s: [1, 0], a: [0, -1], d: [0, 1] };
      if (map[e.key]) { e.preventDefault(); move(map[e.key][0], map[e.key][1]); }
    };
    document.addEventListener('keydown', keyHandler);
    area.querySelector('.u').onclick = function () { move(-1, 0); };
    area.querySelector('.d').onclick = function () { move(1, 0); };
    area.querySelector('.l').onclick = function () { move(0, -1); };
    area.querySelector('.r').onclick = function () { move(0, 1); };
    api.onCleanup(function () { document.removeEventListener('keydown', keyHandler); });
    draw();
  };

  /* ================================================================
     CONTROLLER
     ================================================================ */
  var modal, mount, closeBtn;
  var activeCleanup = [];
  var session = null; // { key, level }

  function runCleanup() { activeCleanup.forEach(function (fn) { try { fn(); } catch (e) {} }); activeCleanup = []; }

  function openModal() { modal.classList.add('show'); modal.setAttribute('aria-hidden', 'false'); }
  function closeModal() { runCleanup(); modal.classList.remove('show'); modal.setAttribute('aria-hidden', 'true'); mount.innerHTML = ''; session = null; }

  function difficultyIndex(l) { return DIFF_LABEL[l - 1]; }

  function playGame(key, startLevel) {
    var s = Store.load();
    var g = s.games[key];
    g.plays = (g.plays || 0) + 1;
    s.stats.gamesPlayed++;
    s.lastPlayed = { key: key, level: startLevel || g.lastLevel || 1, ts: Date.now() };
    s.history.unshift({ key: key, level: s.lastPlayed.level, ts: Date.now() });
    s.history = s.history.slice(0, 20);
    Store.save();
    checkAchievements();
    refreshCards(); refreshKeepPlaying();
    session = { key: key, level: startLevel || g.lastLevel || 1 };
    openModal();
    renderLevel();
  }

  function renderLevel() {
    runCleanup();
    var meta = GAME_META[session.key];
    var s = Store.load(); var g = s.games[session.key];
    mount.innerHTML =
      '<button class="gp-close" id="gpClose">×</button>' +
      '<h2 class="gp-panel-title">' + meta.icon + ' ' + meta.name + '</h2>' +
      '<p class="gp-panel-sub">' + meta.desc + '</p>' +
      '<div class="gp-hud"><div><div class="gp-hud-title">Level ' + session.level + ' / 10</div><div class="gp-hud-sub">' + difficultyIndex(session.level) + '</div></div>' +
      '<div class="gp-dots" id="dots"></div>' +
      '<div class="gp-hud-actions"><button class="gp-mini-btn" id="restart">↺ Restart</button><button class="gp-mini-btn" id="exit">✕ Exit</button></div></div>' +
      '<div class="gp-score-row"><span>🏆 Best: ' + g.bestScore + '</span><span>⭐ Total: ' + g.totalScore + '</span></div>' +
      '<div class="gp-play-area" id="playArea"></div>';
    mount.querySelector('#gpClose').onclick = closeModal;
    mount.querySelector('#exit').onclick = closeModal;
    mount.querySelector('#restart').onclick = renderLevel;
    var dots = mount.querySelector('#dots');
    for (var i = 1; i <= 10; i++) {
      var d = el('button', 'gp-dot', i);
      if (g.completedLevels.indexOf(i) !== -1) d.classList.add('done');
      if (i === session.level) d.classList.add('current');
      if (i <= g.unlockedLevel) { d.classList.add('unlocked'); (function (lvl) { d.onclick = function () { session.level = lvl; renderLevel(); }; })(i); }
      dots.appendChild(d);
    }
    var area = mount.querySelector('#playArea');
    var api = {
      onCleanup: function (fn) { activeCleanup.push(fn); },
      setMsg: function (t) { var m = area.querySelector('.gp-msg'); if (m) m.textContent = t; },
      complete: function (score, extra) { onLevelComplete(score || 0, extra || {}); }
    };
    Games[session.key](area, session.level, api);
  }

  function onLevelComplete(score, extra) {
    runCleanup();
    var s = Store.load(); var g = s.games[session.key];
    var isNew = g.completedLevels.indexOf(session.level) === -1;
    if (isNew) { g.completedLevels.push(session.level); s.stats.levelsCompleted++; }
    g.totalScore += score;
    g.bestScore = Math.max(g.bestScore, score);
    g.unlockedLevel = Math.max(g.unlockedLevel, Math.min(session.level + 1, 10));
    g.lastLevel = session.level;
    s.lastPlayed = { key: session.key, level: session.level, ts: Date.now() };
    Store.save();
    var unlockedAch = checkAchievements();
    refreshCards(); refreshKeepPlaying();

    var area = mount.querySelector('#playArea');
    var overlay = el('div', 'gp-overlay');
    var progressPct = Math.round((g.completedLevels.length / 10) * 100);
    if (session.level >= 10) {
      overlay.innerHTML =
        '<h2>🎉 Game Master!</h2><p>You completed all 10 levels of ' + GAME_META[session.key].name + '!</p>' +
        '<div class="stat-row"><div class="stat"><b>' + g.totalScore + '</b><small>Total Score</small></div><div class="stat"><b>' + g.bestScore + '</b><small>Best Score</small></div><div class="stat"><b>' + progressPct + '%</b><small>Progress</small></div></div>';
    } else {
      overlay.innerHTML =
        '<h2>🎉 Great Job!</h2><p>Level Completed!</p>' +
        '<div class="stat-row"><div class="stat"><b>' + score + '</b><small>Score</small></div><div class="stat"><b>' + progressPct + '%</b><small>Progress</small></div></div>';
    }
    if (unlockedAch.length) {
      unlockedAch.forEach(function (a) {
        overlay.appendChild(el('div', 'gp-unlock', '🏅 Achievement unlocked: ' + a.name));
      });
    }
    var actions = el('div', 'gp-actions');
    var replay = el('button', 'gp-btn secondary', '↺ Replay'); replay.onclick = renderLevel;
    actions.appendChild(replay);
    if (session.level < 10) {
      var nextBtn = el('button', 'gp-btn', 'Next Level →');
      nextBtn.onclick = function () { session.level++; renderLevel(); };
      actions.appendChild(nextBtn);
    }
    var back = el('button', 'gp-btn secondary', 'Back to Games'); back.onclick = closeModal;
    actions.appendChild(back);
    overlay.appendChild(actions);
    area.appendChild(overlay);
  }

  /* ---------------- cards / filters / search ---------------- */
  var cards, filters, searchInput, emptyMsg, grid;
  function refreshCards() {
    var s = Store.load();
    cards.forEach(function (c) {
      var key = c.dataset.game, g = s.games[key];
      var pill = c.querySelector('.gp-progress-pill');
      if (g.completedLevels.length > 0) {
        if (!pill) { pill = el('div', 'gp-progress-pill'); c.querySelector('.gp-card-inner').appendChild(pill); }
        pill.textContent = g.completedLevels.length >= 10 ? '✔ Mastered' : g.completedLevels.length + '/10';
      } else if (pill) pill.remove();
    });
  }
  function applyFilter() {
    var cat = document.querySelector('.gp-filter.active').dataset.category.toLowerCase();
    var q = searchInput.value.toLowerCase().trim();
    var n = 0;
    cards.forEach(function (c) {
      var ok = (cat === 'all' || c.dataset.category.toLowerCase() === cat) && c.dataset.name.toLowerCase().indexOf(q) !== -1;
      c.style.display = ok ? '' : 'none';
      if (ok) n++;
    });
    emptyMsg.hidden = n !== 0;
  }

  /* ---------------- keep playing / quick actions ---------------- */
  var keepEl;
  function refreshKeepPlaying() {
    var s = Store.load();
    if (!s.lastPlayed) { keepEl.innerHTML = '<p style="margin:0;color:#68687b">Pick a game above to start learning through play.</p>'; return; }
    var meta = GAME_META[s.lastPlayed.key];
    var g = s.games[s.lastPlayed.key];
    var pct = Math.round((g.completedLevels.length / 10) * 100);
    keepEl.innerHTML =
      '<div class="gp-keep-info"><div class="gp-keep-thumb">' + meta.icon + '</div><div>' +
      '<h2>' + meta.name + '</h2><small>Level ' + g.lastLevel + ' · Last played ' + timeAgo(s.lastPlayed.ts) + '</small>' +
      '<div class="gp-keep-bar"><span style="width:' + pct + '%"></span></div>' +
      '</div></div><button class="gp-continue" id="continueBtn">▶ Continue Playing</button>';
    keepEl.querySelector('#continueBtn').onclick = function () { playGame(s.lastPlayed.key, g.lastLevel); };
  }
  function timeAgo(ts) {
    var diff = Math.max(0, Date.now() - ts);
    var mins = Math.floor(diff / 60000);
    if (mins < 1) return 'just now';
    if (mins < 60) return mins + 'm ago';
    var hrs = Math.floor(mins / 60);
    if (hrs < 24) return hrs + 'h ago';
    return Math.floor(hrs / 24) + 'd ago';
  }

  function openInfoPanel(title, sub, bodyHtml, wireFn) {
    mount.innerHTML =
      '<button class="gp-close" id="gpClose">×</button>' +
      '<h2 class="gp-panel-title">' + title + '</h2>' +
      (sub ? '<p class="gp-panel-sub">' + sub + '</p>' : '') +
      '<div id="panelBody">' + bodyHtml + '</div>';
    mount.querySelector('#gpClose').onclick = closeModal;
    if (wireFn) wireFn(mount.querySelector('#panelBody'));
    openModal();
  }

  function panelHistory() {
    var s = Store.load();
    if (!s.history.length) return openInfoPanel('↺ History', 'Games you have recently played.', '<p style="text-align:center;color:#68687b">No games played yet — jump into one above!</p>');
    var rows = s.history.map(function (h) {
      var meta = GAME_META[h.key];
      return '<div class="gp-list-row"><span class="ic">' + meta.icon + '</span><div class="meta"><b>' + meta.name + '</b><small>Level ' + h.level + ' · ' + timeAgo(h.ts) + '</small></div></div>';
    }).join('');
    openInfoPanel('↺ History', 'Games you have recently played.', '<div class="gp-list">' + rows + '</div>');
  }
  function panelAchievements() {
    var s = Store.load();
    var rows = ACHIEVEMENTS.map(function (a) {
      var got = !!s.achievements[a.id];
      return '<div class="gp-ach' + (got ? '' : ' locked') + '"><div class="ic">' + a.icon + '</div><b>' + a.name + '</b><small>' + a.desc + '</small></div>';
    }).join('');
    openInfoPanel('🏅 Achievements', 'Unlocked through real gameplay.', '<div class="gp-ach-grid">' + rows + '</div>');
  }
  function panelMyList() {
    var s = Store.load();
    if (!s.myList.length) return openInfoPanel('💗 My List', 'Games you have saved for later.', '<p style="text-align:center;color:#68687b">Your list is empty. Tap the heart on a game card to save it here.</p>');
    var rows = s.myList.map(function (key) {
      var meta = GAME_META[key];
      return '<div class="gp-list-row"><span class="ic">' + meta.icon + '</span><div class="meta"><b>' + meta.name + '</b><small>' + meta.desc + '</small></div><button class="gp-mini-btn" data-play="' + key + '">Play</button></div>';
    }).join('');
    openInfoPanel('💗 My List', 'Games you have saved for later.', '<div class="gp-list">' + rows + '</div>', function (body) {
      body.querySelectorAll('[data-play]').forEach(function (b) { b.onclick = function () { closeModal(); playGame(b.dataset.play); }; });
    });
  }
  function panelDownloads() {
    openInfoPanel('⇩ Downloads', '', '<p style="text-align:center;color:#68687b">Every game runs right in your browser — nothing to download! Play instantly, even offline once the page has loaded.</p>');
  }

  /* ---------------- boot ---------------- */
  document.addEventListener('DOMContentLoaded', function () {
    modal = document.getElementById('gpModal');
    mount = document.getElementById('gpMount');
    cards = Array.prototype.slice.call(document.querySelectorAll('.gp-card'));
    filters = Array.prototype.slice.call(document.querySelectorAll('.gp-filter'));
    searchInput = document.getElementById('gpSearch');
    emptyMsg = document.getElementById('gpEmpty');
    keepEl = document.getElementById('gpKeep');

    modal.addEventListener('click', function (e) { if (e.target === modal) closeModal(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && modal.classList.contains('show')) closeModal(); });

    cards.forEach(function (c) {
      var playBtn = c.querySelector('[data-play]');
      if (playBtn) playBtn.addEventListener('click', function () { playGame(c.dataset.game); });
      var heart = c.querySelector('.gp-fav');
      if (heart) heart.addEventListener('click', function (e) {
        e.stopPropagation();
        var s = Store.load();
        var i = s.myList.indexOf(c.dataset.game);
        if (i === -1) { s.myList.push(c.dataset.game); heart.classList.add('on'); } else { s.myList.splice(i, 1); heart.classList.remove('on'); }
        Store.save();
      });
    });
    filters.forEach(function (f) { f.addEventListener('click', function () { filters.forEach(function (x) { x.classList.remove('active'); }); f.classList.add('active'); applyFilter(); }); });
    if (searchInput) searchInput.addEventListener('input', applyFilter);

    var qMyList = document.getElementById('qaMyList'); if (qMyList) qMyList.onclick = panelMyList;
    var qDownloads = document.getElementById('qaDownloads'); if (qDownloads) qDownloads.onclick = panelDownloads;
    var qHistory = document.getElementById('qaHistory'); if (qHistory) qHistory.onclick = panelHistory;
    var qAchievements = document.getElementById('qaAchievements'); if (qAchievements) qAchievements.onclick = panelAchievements;

    refreshCards();
    refreshKeepPlaying();
    applyFilter();
  });
})();