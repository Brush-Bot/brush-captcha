import React from "react";
import { Table, Tag } from "antd";

const columns = [
  { title: "任务ID", dataIndex: "taskId" },
  { title: "状态", dataIndex: "status", render: (text) => {
      const color = text === "done" ? "green" : text === "waiting" ? "orange" : "blue";
      return <Tag color={color}>{text}</Tag>;
    }},
  { title: "类型", dataIndex: "type" },
  { title: "分配给", dataIndex: "assignedTo" },
  { title: "创建时间", dataIndex: "createdAt" }
];

export default function TaskTable({ data }) {
  return <Table rowKey="taskId" columns={columns} dataSource={data} pagination={false} locale={{ emptyText: "暂无任务" }} />;
}
