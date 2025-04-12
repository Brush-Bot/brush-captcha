import React, { useState } from "react";
import { Button, Input, Card, message } from "antd";
import md5 from "md5";

export default function Login({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = () => {
    const hash = md5(password);
    if (username === "admin" && hash === "21232f297a57a5a743894a0e4a801fc3") {
      localStorage.setItem("token", hash);
      onLogin();
    } else {
      message.error("用户名或密码错误");
    }
  };

  return (
    <Card title="管理员登录" style={{ maxWidth: 300, margin: "100px auto" }}>
      <Input placeholder="用户名" value={username} onChange={e => setUsername(e.target.value)} style={{ marginBottom: 8 }} />
      <Input.Password placeholder="密码" value={password} onChange={e => setPassword(e.target.value)} style={{ marginBottom: 8 }} />
      <Button type="primary" block onClick={handleSubmit}>登录</Button>
    </Card>
  );
}
