# 03 - 3D & WebGL

Used by: Cota Zero Spline ring (3), sneaker/hummingbird (3), tilt cards (5), shader gradients (5).

## Choose
| Option | When | Cost |
|---|---|---|
| **Spline** embed (`@splinetool/react-spline` or `<spline-viewer>`) | Fast designer-made 3D, scroll/mouse events | heavy runtime (~1-4MB), keep scenes light |
| **React Three Fiber + drei** | Real control, GLB models, scroll rigs | build setup |
| **Three.js vanilla** | single page | moderate |
| **OGL / raw shaders** | gradients, noise, distortion | tiny |
| **model-viewer** | simple GLB display + AR | easy |

## Spline scroll binding (Cota Zero ring)
```jsx
import Spline from '@splinetool/react-spline';
export default function Hero(){
  const app = useRef();
  useEffect(()=>{
    const onScroll=()=>{ const obj=app.current?.findObjectByName('Ring');
      if(!obj) return; const p=scrollY/(innerHeight*2);
      obj.rotation.y = p*Math.PI*2; obj.position.y = -p*400; };
    addEventListener('scroll',onScroll,{passive:true}); return ()=>removeEventListener('scroll',onScroll);
  },[]);
  return <Spline scene="https://prod.spline.design/XXXX/scene.splinecode" onLoad={a=>app.current=a}
     style={{position:'fixed',inset:0,zIndex:0}}/>;
}
```
Put text above with `position:relative; z-index:1`. In Spline: export the scene URL, name the objects you animate.
No Spline account? Recreate ring with Three: N `BoxGeometry` slabs placed in a circle, tilted, `MeshStandardMaterial` warm metal + `Environment`.

## R3F scroll-driven model (template)
```jsx
import {Canvas,useFrame} from '@react-three/fiber';
import {useGLTF,Environment,ContactShadows,ScrollControls,useScroll} from '@react-three/drei';
function Model(){ const {scene}=useGLTF('/shoe.glb'); const s=useScroll();
  useFrame((st)=>{ const r=s.offset; scene.rotation.y=r*Math.PI*2 + st.pointer.x*.3;
     scene.position.y=Math.sin(st.clock.elapsedTime)*.05; scene.rotation.x=st.pointer.y*.15; });
  return <primitive object={scene} scale={1.4}/> }
<Canvas camera={{position:[0,0,4],fov:35}} dpr={[1,2]}>
  <ScrollControls pages={4} damping={0.2}><Model/></ScrollControls>
  <Environment preset="studio"/><ContactShadows opacity={.4} blur={2.5}/>
</Canvas>
```
Sync HTML text via `<Scroll html>` from drei.

## Getting 3D models
- Generate: Meshy, Tripo, Rodin, Hunyuan3D (image->GLB). Optimize with `gltf-transform optimize in.glb out.glb --compress draco --texture-compress webp`.
- Free: Sketchfab (check license CC-BY), Poly Haven (CC0), Quaternius (CC0).
- Target < 2MB GLB, textures 1024-2048.

## Mouse-reactive 3D object over giant background type (sneaker "DUNK")
Layering: z0 giant text (`font-size:28vw`, color slightly darker than bg), z1 canvas transparent (`alpha:true`), z2 UI. Model follows pointer with lerp (`damp`), float idle animation, soft shadow on ground.

## Shader background (animated gradient / light rays)
Minimal fullscreen fragment shader with OGL or Three `ShaderMaterial`; uniforms `uTime`, `uMouse`, `uColors`. Libraries: `@paper-design/shaders-react` (mesh gradient, grain), Shader Gradient, Spell UI `animated-gradient`, `light-rays` (OGL). Add film grain overlay (SVG feTurbulence) for premium feel.

## Gaussian splats / photoreal rooms
For house tours: Luma AI / Polycam splat -> `@mkkellogg/gaussian-splats-3d` or PlayCanvas SuperSplat; camera path animated with GSAP on scroll. Heavier than frames; prefer frame sequences unless free-roam is needed.

## Rules
- `dpr={[1,2]}`, `frameloop="demand"` when static, dispose geometries, pause offscreen (`IntersectionObserver`).
- Provide poster image while loading; lazy-load canvas below the fold.
- Mobile: lower DPR, disable post-processing.
