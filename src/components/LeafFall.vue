<template>
  <div style="position: absolute; min-width: 100%">
    <section>
      <!-- Hiệu ứng lá -->
      <div class="leaves">
        <div class="set">
          <div><img src="@/assets/leaf_01.png" /></div>
          <div><img src="@/assets/leaf_02.png" /></div>
          <div><img src="@/assets/leaf_03.png" /></div>
          <div><img src="@/assets/leaf_04.png" /></div>
          <div><img src="@/assets/leaf_05.png" /></div>
          <div><img src="@/assets/leaf_06.png" /></div>
          <div><img src="@/assets/leaf_07.png" /></div>
          <div><img src="@/assets/leaf_01.png" /></div>
          <div><img src="@/assets/leaf_02.png" /></div>
          <div><img src="@/assets/leaf_03.png" /></div>
          <div><img src="@/assets/leaf_04.png" /></div>
          <div><img src="@/assets/leaf_05.png" /></div>
          <div><img src="@/assets/leaf_07.png" /></div>
          <div><img src="@/assets/leaf_06.png" /></div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
section {
  position: relative;
  width: 100%;
  height: 93vh;
  overflow: hidden;
  /* background: #e0f7fa; */
}

.leaves {
  position: absolute;
  top: -10%;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  pointer-events: none;
  z-index: 1;
}

.leaves .set {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.leaves .set div {
  position: absolute;
  display: block;
}

/* Kích thước ảnh lá */
.leaves .set div img {
  width: 60px;
  height: auto;
  opacity: 0.8;
}

/* Hiệu ứng lá rơi */
@keyframes animate {
  0% {
    top: -10%;
    transform: translateX(20px) rotate(0deg);
  }
  10% {
    opacity: 1;
    transform: translateX(20px) rotate(45deg);
  }
  20% {
    transform: translateX(-20px) rotate(90deg);
  }
  40% {
    transform: translateX(20px) rotate(180deg);
  }
  60% {
    transform: translateX(-20px) rotate(225deg);
  }
  100% {
    top: 110%;
    transform: translateX(20px) rotate(225deg);
  }
}

/* Vị trí và thời gian cho từng chiếc lá */
.leaves .set div:nth-child(1) {
  left: 20%;
  animation: animate 20s linear infinite;
  animation-delay: 0s;
}
.leaves .set div:nth-child(2) {
  left: 40%;
  animation: animate 25s linear infinite;
  animation-delay: 2s;
}
.leaves .set div:nth-child(3) {
  left: 60%;
  animation: animate 15s linear infinite;
  animation-delay: 1s;
}
.leaves .set div:nth-child(4) {
  left: 80%;
  animation: animate 18s linear infinite;
  animation-delay: 3s;
}
.leaves .set div:nth-child(5) {
  left: 10%;
  animation: animate 12s linear infinite;
  animation-delay: 0.5s;
}
.leaves .set div:nth-child(6) {
  left: 30%;
  animation: animate 16s linear infinite;
  animation-delay: 1.5s;
}
.leaves .set div:nth-child(7) {
  left: 50%;
  animation: animate 22s linear infinite;
  animation-delay: 0.8s;
}
.leaves .set div:nth-child(8) {
  left: 70%;
  animation: animate 14s linear infinite;
  animation-delay: 2.5s;
}
.leaves .set div:nth-child(9) {
  left: 15%;
  animation: animate 19s linear infinite;
  animation-delay: 1s;
}
.leaves .set div:nth-child(10) {
  left: 35%;
  animation: animate 21s linear infinite;
  animation-delay: 3s;
}
.leaves .set div:nth-child(11) {
  left: 55%;
  animation: animate 17s linear infinite;
  animation-delay: 1.2s;
}
.leaves .set div:nth-child(12) {
  left: 75%;
  animation: animate 23s linear infinite;
  animation-delay: 2.2s;
}
.leaves .set div:nth-child(13) {
  left: 25%;
  animation: animate 20s linear infinite;
  animation-delay: 0.6s;
}
.leaves .set div:nth-child(14) {
  left: 85%;
  animation: animate 18s linear infinite;
  animation-delay: 1.8s;
}
</style>
