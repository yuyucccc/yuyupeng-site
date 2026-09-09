(() => {
  if(customElements.get('personal-logo-fusion'))return;
  const outer='M 0 0 C 14.574 -16.75 36.047 -27.338 59.993 -27.338 C 103.896 -27.338 139.487 8.252 139.487 52.155 C 139.487 96.058 103.896 131.648 59.993 131.648 C 36.047 131.648 14.574 121.06 0 104.31 L 0.002 104.309 C -14.572 121.06 -36.046 131.648 -59.993 131.648 C -103.896 131.648 -139.486 96.058 -139.486 52.155 C -139.486 8.252 -103.896 -27.338 -59.993 -27.338 C -36.046 -27.338 -14.572 -16.749 0.002 0.001';
  const inner='M 0 0 C 12.415 -14.269 30.707 -23.288 51.106 -23.288 C 88.505 -23.288 118.823 7.03 118.823 44.429 C 118.823 81.828 88.505 112.146 51.106 112.146 C 30.707 112.146 12.415 103.127 0 88.858 L 0.001 88.857 C -12.414 103.126 -30.706 112.146 -51.106 112.146 C -88.505 112.146 -118.823 81.828 -118.823 44.429 C -118.823 7.03 -88.505 -23.288 -51.106 -23.288 C -30.706 -23.288 -12.414 -14.268 0.001 0.001';
  const clamp=(n,min,max,fallback)=>Number.isFinite(n)?Math.min(max,Math.max(min,n)):fallback;
  class PersonalLogoFusion extends HTMLElement {
    static get observedAttributes(){return ['duration','minimum','paused','fill-strength'];}
    constructor(){super();this.attachShadow({mode:'open'});this.animations=[];this.visible=true;this.visibilityChange=()=>this.sync();this.reduceChange=()=>this.render();}
    connectedCallback(){
      this.reduced=matchMedia('(prefers-reduced-motion: reduce)');this.reduced.addEventListener('change',this.reduceChange);
      document.addEventListener('visibilitychange',this.visibilityChange);
      this.observer=new IntersectionObserver(entries=>{this.visible=entries[0].isIntersecting;this.sync();});this.observer.observe(this);this.render();
    }
    disconnectedCallback(){this.animations.forEach(a=>a.cancel());this.animations=[];this.observer?.disconnect();this.reduced?.removeEventListener('change',this.reduceChange);document.removeEventListener('visibilitychange',this.visibilityChange);}
    attributeChangedCallback(name){if(!this.isConnected||!this.reduced)return;if(name==='paused'){this.sync();return;}if(name==='duration'){const rate=6/this.duration;this.animations.forEach(a=>a.updatePlaybackRate(rate));return;}if(name==='fill-strength'){this.updateFill();return;}this.render(true);}
    get duration(){return clamp(Number(this.getAttribute('duration')??6),3,12,6);}
    get minimum(){return clamp(Number(this.getAttribute('minimum')??.32),.15,.8,.32);}
    updateFill(){this.shadowRoot.querySelector('.fill-layer')?.style.setProperty('opacity',String(clamp(Number(this.getAttribute('fill-strength')??.75),0,1,.75)));}
    render(preserve=false){
      const time=preserve?(this.animations[0]?.currentTime||0):0;
      this.animations.forEach(a=>a.cancel());this.animations=[];
      const outline=(which,d,y,r)=>{
        const gradient=which==='outer'
          ? `<linearGradient id="outer" gradientUnits="userSpaceOnUse" x1="-139.487" y1="0" x2="139.487" y2="0" color-interpolation="sRGB">
              <stop offset="0" stop-color="#ffffff" stop-opacity=".72"/>
              <stop offset=".18" stop-color="#dce0e1" stop-opacity=".82"/>
              <stop offset=".34" stop-color="#73797b" stop-opacity=".94"/>
              <stop offset=".5" stop-color="#030405" stop-opacity="1"/>
              <stop offset=".66" stop-color="#73797b" stop-opacity=".94"/>
              <stop offset=".82" stop-color="#dce0e1" stop-opacity=".82"/>
              <stop offset="1" stop-color="#ffffff" stop-opacity=".72"/>
            </linearGradient>`
          : `<radialGradient id="inner" gradientUnits="userSpaceOnUse" cx="0" cy="${y}" r="${r}"><stop offset="0" style="stop-color:var(--fusion-ring-dim)"/><stop offset=".38" style="stop-color:var(--fusion-ring-dim)"/><stop offset=".7" style="stop-color:var(--fusion-ring-mid)"/><stop offset="1" style="stop-color:var(--fusion-ring-bright)"/></radialGradient>`;
        return `<svg viewBox="-210 -155 420 310" aria-hidden="true"><defs>${gradient}</defs><path d="${d}" transform="translate(0 ${y}) scale(1 -1)" fill="none" stroke="url(#${which})" stroke-width="${which==='outer'?3:1.7}" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
      };
      this.shadowRoot.innerHTML=`<style>
        :host{display:inline-block;width:420px;height:310px;max-width:100%;--fusion-ring-dim:light-dark(#bcc2c0,#3b4447);--fusion-ring-mid:light-dark(#748082,#aab4b6);--fusion-ring-bright:light-dark(#263234,#f7ffff);}
        .scene{position:relative;width:100%;height:100%;perspective:680px;perspective-origin:50% 50%;transform-style:preserve-3d;}
        .layer{position:absolute;inset:0;width:100%;height:100%;transform-origin:center center;backface-visibility:visible;}
        .outer-layer{transform-style:preserve-3d;will-change:transform;}
        .fill-layer{will-change:transform;}
        svg{display:block;width:100%;height:100%;overflow:visible;pointer-events:none;}
      </style><div class="scene" role="img" aria-label="旋转外环与内部径向渐变组成的个人标志">
        <div class="layer fill-layer"><svg viewBox="-210 -155 420 310" aria-hidden="true"><defs>
          <radialGradient id="clear-fill" gradientUnits="userSpaceOnUse" cx="0" cy="44.429" r="96.7071991" color-interpolation="sRGB">
            <stop offset="0" stop-color="#000000"/>
            <stop offset=".125" stop-color="#131313"/>
            <stop offset=".25" stop-color="#2b2b2b"/>
            <stop offset=".375" stop-color="#4a4a4a"/>
            <stop offset=".5" stop-color="#6e6e6e"/>
            <stop offset=".625" stop-color="#919191"/>
            <stop offset=".75" stop-color="#b5b5b5"/>
            <stop offset=".875" stop-color="#dadada"/>
            <stop offset=".997963" stop-color="#ffffff"/>
          </radialGradient></defs><path d="${inner}" transform="translate(0 44.429) scale(1 -1)" fill="url(#clear-fill)"/></svg></div>
        <div class="layer outer-layer">${outline('outer',outer,52.155,114.972)}</div>
      </div>`;
      this.updateFill();
      if(this.reduced.matches)return;
      const ring=this.shadowRoot.querySelector('.outer-layer');
      const fill=this.shadowRoot.querySelector('.fill-layer');
      this.animations=[
        ring.animate([{transform:'rotateX(0deg)'},{transform:'rotateX(360deg)'}],{duration:6000,iterations:Infinity,easing:'linear'}),
        fill.animate([{transform:'scale(1)'},{transform:`scale(${this.minimum})`,offset:.5},{transform:'scale(1)'}],{duration:6000,iterations:Infinity,easing:'ease-in-out'})
      ];
      this.animations.forEach(a=>{a.currentTime=time;a.playbackRate=6/this.duration;});this.sync();
    }
    sync(){const stopped=this.hasAttribute('paused')||!this.visible||document.hidden||this.reduced?.matches;this.animations.forEach(a=>stopped?a.pause():a.play());}
  }
  customElements.define('personal-logo-fusion',PersonalLogoFusion);
})();
