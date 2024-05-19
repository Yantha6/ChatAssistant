from colorama import Fore, Style

def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"{Fore.GREEN}调用函数：{func.__name__}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}返回值：{result}{Style.RESET_ALL}")
        return result
    return wrapper