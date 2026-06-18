# -*- coding: utf-8 -*-
import logging
import sys
import re

class FastAPILogFormatter(logging.Formatter):
    """Enterprise FastAPI/Uvicorn style formatter with strict brand tracking and conditional code coloring."""
    
    # ANSI Color Escape Codes
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    BLUE = "\033[34m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    def format(self, record: logging.LogRecord) -> str:
        # Step 1: Format Timestamp in Cyan
        time_str = f"{self.CYAN}{self.formatTime(record, '%Y-%m-%d %H:%M:%S')}{self.RESET}"
        
        # Step 2: Color ONLY the Level bracket
        if record.levelno >= logging.ERROR:
            level_tag = f"{self.RED}{self.BOLD}[{record.levelname}]{self.RESET}"
        elif record.levelno == logging.WARNING:
            level_tag = f"{self.YELLOW}[{record.levelname}]{self.RESET}"
        else:
            level_tag = f"{self.GREEN}[{record.levelname}]{self.RESET}"

        # Step 3: Handle Status Codes dynamically from message text or extra parameters
        message = record.getMessage()
        
        # Pull explicit code from extra context if available
        explicit_code = str(getattr(record, "status_code", ""))
        
        # Check if the message contains bracketed codes or if an extra status code was passed
        status_tag = ""
        
        # Pattern to look for any brackets containing numbers or status strings (e.g., [200 OK], [404], [500])
        bracket_match = re.search(r'\[([a-zA-Z0-9\s_]+)\]', message + " " + explicit_code)
        
        if bracket_match:
            full_tag = bracket_match.group(0)   # Extract e.g., "[200 OK]" or "[404]"
            content = bracket_match.group(1)    # Extract e.g., "200 OK" or "404"
            
            # Clean the tag out of the main message so it doesn't print twice
            message = message.replace(full_tag, "").strip(" .-_")
            
            # Color logic: Green for 200 variations, Red for anything else
            if "200" in content:
                status_tag = f" {self.GREEN}{full_tag}{self.RESET}"
            else:
                status_tag = f" {self.RED}{self.BOLD}{full_tag}{self.RESET}"

        # Step 4: Force ALL variations of the brand name to be Bold Blue everywhere (including inside parentheses)
        base_log_line = f"{time_str} {level_tag} ({record.name}): {message}{status_tag}"
        
        brand_pattern = re.compile(r'(vllm[-_]sdk)', re.IGNORECASE)
        final_colored_line = brand_pattern.sub(f"{self.BLUE}{self.BOLD}\\1{self.RESET}", base_log_line)
        
        return final_colored_line

def setup_sdk_logging():
    """Attaches the refined FastAPI formatter to the system stream pipe."""
    root_logger = logging.getLogger()
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)
            
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(FastAPILogFormatter())
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)