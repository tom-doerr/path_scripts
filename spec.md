# Aider Code Change Specification

## *SEARCH/REPLACE* Block Formatting Rules

1. **File Path**  
   Must be the full path on its own line with no formatting:
   ```
   path/to/file.py
   ```

2. **Code Fences**  
   Use quadruple backticks with language identifier:
   ````python
   ```` 

3. **Block Structure**  
   Exact sequence:
   ```
   <<<<<<< SEARCH
   [existing code]
   def new_function():
       print("Created!")
