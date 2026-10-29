"""Run with: python -m streamlit run app.py"""
import os
import streamlit as st
from core import complete, make_messages

st.set_page_config(page_title="知伴 · AI 期末伴学", page_icon="📚", layout="wide")
st.title("知伴 · AI 期末伴学")
st.caption("为有编程基础的大三学生，把复习拆成可以完成的小步。")
st.session_state.setdefault("conversations", {})

with st.sidebar:
    st.header("本次复习")
    course = st.text_input("课程", "数据结构与算法", max_chars=100)
    material = st.text_area("粘贴课程资料", height=220, max_chars=20000,
                            placeholder="例如：课程大纲、笔记或老师给出的考试范围……")
    st.caption("最多 20000 字。提问时，资料与近期对话会发送到 DeepSeek。")
    st.caption("资料引用的行号对应下方的资料预览。")
    with st.expander("资料行号预览"):
        st.code("\n".join(f"{i}: {line}" for i, line in enumerate(material.splitlines(), 1)) or "暂无资料")
    st.caption("模型：" + os.getenv("DEEPSEEK_MODEL", "deepseek-flash"))
    ready = bool(os.getenv("DEEPSEEK_API_KEY", "").strip())
    if ready:
        st.success("已读取密钥配置，尚未验证连接")
    else:
        st.info("尚未配置 DEEPSEEK_API_KEY，可先查看界面。")

mode = st.radio("今天从哪里开始？", ["复习计划", "分步答疑", "自测与反馈"], horizontal=True, index=1)
# Separate histories by material, course and mode; old course data is never sent in a new course.
context = (course, material, mode)
if st.session_state.get("active_context") != context:
    st.session_state.conversations = {mode: []}
    st.session_state.active_context = context
history = st.session_state.conversations.setdefault(mode, [])

if st.button("清空当前对话"):
    history.clear()
    st.rerun()

question = None
if mode == "复习计划":
    with st.form("plan"):
        days = st.number_input("距离考试还有几天", min_value=1, max_value=90, value=7)
        minutes = st.number_input("每天可用分钟", min_value=15, max_value=480, value=60, step=15)
        goal = st.text_input("复习目标与薄弱点", "理解基本概念，掌握常见算法题", max_chars=1000)
        if st.form_submit_button("生成复习计划", disabled=not ready):
            question = (f"请制定 {days} 天、每天 {minutes} 分钟的复习计划。目标：{goal}。"
                        "每天列出知识点、具体练习、时间分配和自检方式。根据资料界定范围；无资料时标注为建议范围。")
elif mode == "自测与反馈":
    st.info("先做题，再提交自己的答案；AI 会给出反馈。")
    if st.button("开始一轮自测", disabled=not ready):
        question = "请围绕当前课程出 3 道难度递进的自测题，包含至少一道代码阅读题。先只给题目，不给答案，等我作答后逐题反馈并指出需要复习的概念。"
else:
    st.info("可以贴出疑问或代码。助手会先给提示；需要完整讲解时直接告诉它。")

for message in history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

typed = st.chat_input("输入问题、代码或自测答案……", disabled=not ready, max_chars=8000)
question = typed or question
if question:
    with st.chat_message("user"):
        st.markdown(question)
    try:
        with st.spinner("正在整理思路，请稍候……"):
            answer = complete(make_messages(course, material, history, question, mode))
        history.extend([{"role": "user", "content": question}, {"role": "assistant", "content": answer}])
        with st.chat_message("assistant"):
            st.markdown(answer)
    except (ValueError, RuntimeError) as exc:
        st.error(str(exc))
        st.caption("本次请求未加入对话，可重新提交。")

if history:
    transcript = "\n\n".join(f"【{m['role']}】\n{m['content']}" for m in history)
    st.download_button("下载本次复习记录", transcript, file_name="复习记录.md", mime="text/markdown")
st.caption("当前为单人原型：会话不写入数据库，重启后不保证保留。AI 的讲解和资料引用需要核对。")
