import React, { useEffect, useState } from "react";
import { Table, Tag, Row, Col, Card } from "antd";

const columns = [
    { title: "ID", dataIndex: "id" },
    { title: "IP", dataIndex: "ip" },
    {
        title: "状态",
        dataIndex: "status",
        render: (text) => {
            const color = text === "空闲" ? "green" : text === "忙碌" ? "red" : "orange";
            return <Tag color={color}>{text}</Tag>;
        }
    },
    {
        title: <div style={{ textAlign: "center" }}>容量 / 总任务 / 排队</div>,
        render: (_, r) => {
            const total = r.max_concurrency;
            const running = r.pending_tasks;
            const pending = r.current_tasks - r.pending_tasks;
            const current = running + pending;
            const isOverload = current > total;

            const blocks = [];

            for (let i = 0; i < Math.max(total, current); i++) {
                let color = "#e5e5ea"; // 空闲灰（浅）

                if (i < current) {
                    color = i < running ? "#5ac8fa" : "#ffd60a";
                    if (isOverload) color = "#ff3b30";
                }

                blocks.push(
                    <div
                        key={i}
                        style={{
                            width: 6,
                            height: 14,
                            marginRight: 1,
                            backgroundColor: color,
                            borderRadius: 2
                        }}
                    />
                );
            }

            return (
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                    <div
                        style={{
                            display: "flex",
                            flexWrap: "wrap",
                            padding: "2px 6px",
                            borderRadius: 4,
                            backgroundColor: "rgba(255,255,255,0.08)",
                            justifyContent: "center"
                        }}
                    >
                        {blocks}
                    </div>
                    <div style={{ fontSize: 12, marginTop: 4, color: "#999" }}>
                        {total}/{current}/{pending}
                    </div>
                </div>
            );
        }
    },
    {
        title: "任务类型",
        dataIndex: "task_types",
        render: (tags) =>
          Array.isArray(tags)
            ? tags.map((t) => <Tag key={t}>{t}</Tag>)
            : null
    },
    { title: "上线时间", dataIndex: "connected_at" },
    { title: "Uptime", dataIndex: "uptime" }
];

export default function WorkerTable({ data, taskSummary }) {
    const { total, completed, pending, assigned } = taskSummary || {};

    return (
        <div>
            {/* 任务统计区 */}
            <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
                <Col span={6}>
                    <Card title="总任务数" bordered={false} style={{ textAlign: "center" }}>
                        <div style={{ fontSize: 18, fontWeight: 600 }}>{total ?? "-"}</div>
                    </Card>
                </Col>
                <Col span={6}>
                    <Card title="已完成" bordered={false} style={{ textAlign: "center" }}>
                        <div style={{ fontSize: 18, fontWeight: 600 }}>{completed ?? "-"}</div>
                    </Card>
                </Col>
                <Col span={6}>
                    <Card title="进行中" bordered={false} style={{ textAlign: "center" }}>
                        <div style={{ fontSize: 18, fontWeight: 600 }}>{pending ?? "-"}</div>
                    </Card>
                </Col>
                <Col span={6}>
                    <Card title="已分配" bordered={false} style={{ textAlign: "center" }}>
                        <div style={{ fontSize: 18, fontWeight: 600 }}>{assigned ?? "-"}</div>
                    </Card>
                </Col>
            </Row>

            {/* 节点表格 */}
            <Table
                rowKey="id"
                columns={columns}
                dataSource={data}
                pagination={false}
                locale={{ emptyText: "暂无节点信息" }}
                style={{ marginTop: 8 }}
            />
        </div>
    );
}