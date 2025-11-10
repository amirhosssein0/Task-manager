"use client";

import { useEffect, useState } from "react";

export default function Home() {
  const [msg, setMsg] = useState("Connecting backend ...");

  useEffect(() => {
    fetch("http://127.0.0.1:8085/")
      .then(res => res.json())
      .then(data => setMsg(data.message))
      .catch(err => setMsg("❌Django failed"));
  }, []);

  return (
    <main className="flex min-h-screen items-center justify-center">
      <h1 className="text-2xl font-bold">{msg}</h1>
    </main>
  );
}
