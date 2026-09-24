"use client";

import { useMemo, useRef } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Grid } from "@react-three/drei";
import * as THREE from "three";

function Particles({ count = 900 }: { count?: number }) {
  const points = useRef<THREE.Points>(null);
  const positions = useMemo(() => {
    const array = new Float32Array(count * 3);
    for (let i = 0; i < count; i += 1) {
      array[i * 3] = (Math.random() - 0.5) * 46;
      array[i * 3 + 1] = Math.random() * 10 + 0.2;
      array[i * 3 + 2] = (Math.random() - 0.5) * 46;
    }
    return array;
  }, [count]);

  useFrame(({ clock }) => {
    if (!points.current) return;
    points.current.rotation.y = clock.elapsedTime * 0.01;
    points.current.position.y = Math.sin(clock.elapsedTime * 0.12) * 0.12;
  });

  return (
    <points ref={points} frustumCulled={false}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
      </bufferGeometry>
      <pointsMaterial
        color="#ffffff"
        size={0.028}
        sizeAttenuation
        transparent
        opacity={0.32}
        depthWrite={false}
      />
    </points>
  );
}

function MouseRig() {
  const light = useRef<THREE.PointLight>(null);
  const { camera, pointer } = useThree();

  useFrame(() => {
    camera.position.x = THREE.MathUtils.lerp(camera.position.x, pointer.x * 1.35, 0.035);
    camera.position.y = THREE.MathUtils.lerp(camera.position.y, 6.4 + pointer.y * 0.45, 0.035);
    camera.lookAt(0, 0.6, 0);

    if (light.current) {
      light.current.position.x = THREE.MathUtils.lerp(
        light.current.position.x,
        pointer.x * 8,
        0.08,
      );
      light.current.position.z = THREE.MathUtils.lerp(
        light.current.position.z,
        -pointer.y * 6,
        0.08,
      );
    }
  });

  return (
    <pointLight
      ref={light}
      intensity={22}
      distance={22}
      decay={2}
      color="#ffffff"
      position={[0, 7, 3]}
    />
  );
}

function Scene() {
  return (
    <>
      <color attach="background" args={["#000000"]} />
      <fog attach="fog" args={["#000000", 10, 38]} />
      <ambientLight intensity={0.06} />
      <MouseRig />
      <Grid
        position={[0, 0, 0]}
        args={[40, 40]}
        infiniteGrid
        fadeDistance={26}
        fadeStrength={1.4}
        cellSize={0.55}
        cellThickness={0.45}
        cellColor="#2a2a2e"
        sectionSize={2.75}
        sectionThickness={0.95}
        sectionColor="#3f3f46"
      />
      <Particles />
    </>
  );
}

export default function HeroScene() {
  return (
    <Canvas
      camera={{ position: [0, 6.4, 13.5], fov: 40, near: 0.1, far: 80 }}
      dpr={[1, 1.5]}
      gl={{ antialias: true, alpha: false, powerPreference: "high-performance" }}
    >
      <Scene />
    </Canvas>
  );
}
