import { ConfigProvider, Dropdown, Input, theme, type MenuProps } from "antd";
import zhCN from "antd/locale/zh_CN";
import {
  type MenuDataItem,
  PageContainer,
  ProLayout,
} from "@ant-design/pro-components";
import { UserOutlined } from "@ant-design/icons";
import { Link, Outlet, useLocation } from "react-router-dom";
import "@/styles/home.css";
import ComplianceFooter from "./ComplianceFooter";
import "./common.css";

const NAV_ITEMS: MenuDataItem[] = [
  { key: "/", name: "市场复盘", path: "/" },
  { key: "/stock", name: "个股分析", path: "/stock" },
  { key: "/qa", name: "AI问答", path: "/qa" },
  { key: "/watch-list", name: "自选股", path: "/watch-list" },
];

const USER_MENU_ITEMS: MenuProps["items"] = [
  { key: "profile", label: "个人中心" },
  { key: "logout", label: "退出登录" },
];

/**
 * 基于 ProLayout 的全局布局。
 *
 * Header（顶部导航 / 搜索 / 头像）与 Footer 在此处统一渲染，
 * 各路由页面通过 Outlet 渲染到内容区，保证任意页面布局一致。
 */
export default function LayoutContainer() {
  const location = useLocation();

  const handleSearch = (value: string) => {
    // 预留：后续接入股票搜索接口后再发起请求。
    void value;
  };

  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: "#36cfc9",
          colorBgLayout: "#071018",
          borderRadius: 10,
        },
      }}
    >
      <ProLayout
        title="A股 AI"
        locale="zh-CN"
        logo={<span className="brand-mark" aria-hidden="true" />}
        layout="top"
        contentWidth="Fluid"
        fixedHeader
        fixSiderbar
        navTheme="realDark"
        location={location}
        token={{
          header: {
            colorBgHeader: "rgba(7, 16, 24, .92)",
            colorBgScrollHeader: "rgba(7, 16, 24, .92)",
            colorBgMenuItemSelected: "#11242f",
            colorTextMenuSelected: "var(--text)",
          },
        }}
        menuDataRender={() => NAV_ITEMS}
        menuItemRender={(item, dom) => <Link to={item.path || "/"}>{dom}</Link>}
        actionsRender={() => [
          <Input.Search
            key="search"
            placeholder="搜索股票 / 代码"
            allowClear
            onSearch={handleSearch}
          />,
        ]}
        avatarProps={{
          icon: <UserOutlined />,
          size: "small",
          title: "用户",
          render: (_props, dom) => (
            <Dropdown menu={{ items: USER_MENU_ITEMS }} placement="bottomRight">
              {dom}
            </Dropdown>
          ),
        }}
        contentStyle={{
          backgroundColor: "var(--bg)",
          paddingBottom: 64,
        }}
        footerRender={() => <ComplianceFooter />}
      >
        <PageContainer title={false}>
          <Outlet />
        </PageContainer>
      </ProLayout>
    </ConfigProvider>
  );
}
