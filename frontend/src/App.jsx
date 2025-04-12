import React, { useEffect, useState } from "react";
import {
  Layout,
  Typography,
  Divider,
  Alert,
  Switch,
  Button,
  ConfigProvider,
  theme,
} from "antd";
import { useNavigate } from "react-router-dom";
import WorkerTable from "./components/WorkerTable";
import TaskTable from "./components/TaskTable";
import { fetchNodes, fetchTasks } from "./api";

const { Title } = Typography;
const { Header, Content } = Layout;
const { defaultAlgorithm, darkAlgorithm } = theme;

export default function App() {
  const prefersDark = window.matchMedia?.("(prefers-color-scheme: dark)").matches;
  const [isDark, setIsDark] = useState(() => {
    const saved = localStorage.getItem("theme");
    return saved ? saved === "dark" : prefersDark;
  });

  const [workers, setWorkers] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [taskSummary, setTaskSummary] = useState({});
  const [hasError, setHasError] = useState(false);
  const navigate = useNavigate();

  const load = async () => {
    try {
      const [nodeRes, taskRes] = await Promise.all([fetchNodes(), fetchTasks()]);
      setWorkers(Array.isArray(nodeRes.data) ? nodeRes.data : []);
      setTasks(Array.isArray(taskRes.data?.tasks) ? taskRes.data.tasks : []);
      setTaskSummary(taskRes.data?.summary || {});
      setHasError(false);
    } catch (err) {
      console.error("❌ 数据加载失败:", err.message);
      setWorkers([]);
      setTasks([]);
      setTaskSummary({});
      setHasError(true);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token !== "21232f297a57a5a743894a0e4a801fc3") {
      navigate("/login");
    }
    load();
    const interval = setInterval(load, 30000);
    return () => clearInterval(interval);
  }, [navigate]);

  const handleThemeSwitch = (checked) => {
    setIsDark(checked);
    localStorage.setItem("theme", checked ? "dark" : "light");
  };

  return (
      <ConfigProvider theme={{ algorithm: isDark ? darkAlgorithm : defaultAlgorithm }}>
        <Layout style={{ padding: 24 }}>
          <Header
              style={{
                background: "transparent",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
          >
            <Title level={3} style={{ margin: 0 }}>
              Capsolver 节点监控
            </Title>
            <div>
              <Switch
                  checkedChildren="深色"
                  unCheckedChildren="亮色"
                  checked={isDark}
                  onChange={handleThemeSwitch}
                  style={{ marginRight: 12 }}
              />
              <Button
                  danger
                  size="small"
                  onClick={() => {
                    localStorage.removeItem("token");
                    window.location.reload();
                  }}
              >
                退出
              </Button>
            </div>
          </Header>

          <Content>
            {hasError && (
                <Alert
                    message="后端服务异常"
                    type="error"
                    showIcon
                    style={{ margin: "16px 0" }}
                />
            )}

            <Divider orientation="left">节点状态</Divider>
            <WorkerTable data={workers} taskSummary={taskSummary} />

            <Divider orientation="left">任务队列</Divider>
            <TaskTable data={tasks} />
          </Content>
        </Layout>
      </ConfigProvider>
  );
}