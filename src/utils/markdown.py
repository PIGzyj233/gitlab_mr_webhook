class Markdown:
    def __init__(self, text: str = ""):
        self.val = text or ""
    
    def __add__(self, other) -> 'Markdown':
        """使用 + 运算符连接文本"""
        if isinstance(other, Markdown):
            self.val += other.val
        elif isinstance(other, str):
            self.val += other
        else:
            raise TypeError(f"unsupported operand type(s) for +: '{type(self).__name__}' and '{type(other).__name__}'")
        return self
    
    def new_line(self) -> 'Markdown':
        """添加换行"""
        self.val = f"{self.val}\n"
        return self
    
    def quote(self) -> 'Markdown':
        """添加引用"""
        self.val = f">{self.val}"
        return self
    
    def bold(self) -> 'Markdown':
        """加粗文本"""
        self.val = f"**{self.val}**"
        return self
    
    def info(self) -> 'Markdown':
        """信息颜色"""
        self.val = f"<font color='info'>{self.val}</font>"
        return self
    
    def warning(self) -> 'Markdown':
        """警告颜色"""
        self.val = f"<font color='warning'>{self.val}</font>"
        return self
    
    def comment(self) -> 'Markdown':
        """注释颜色"""
        self.val = f"<font color='comment'>{self.val}</font>"
        return self
    
    def error(self) -> 'Markdown':
        """错误颜色"""
        self.val = f"<font color='error'>{self.val}</font>"
        return self
        
    def success(self) -> 'Markdown':
        """成功颜色"""
        self.val = f"<font color='success'>{self.val}</font>"
        return self
    
    def mark(self) -> 'Markdown':
        """@某人"""
        self.val = f"<@{self.val}>"
        return self
    
    def __str__(self) -> str:
        return self.val
    
    def __repr__(self) -> str:
        return self.val

def md(text: str = "") -> Markdown:
    """创建Markdown实例的工厂函数"""
    if text and not isinstance(text, str):
        raise TypeError("expected arg not string")
    return Markdown(text) 