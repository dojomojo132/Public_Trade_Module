{
  "tools": [
    {
      "name": "start_1c_debug_session",
      "description": "Запускает сеанс отладки 1С",
      "inputSchema": {
        "type": "object",
        "properties": {
          "infobase": {
            "type": "string",
            "description": "Строка подключения к базе"
          },
          "user": {
            "type": "string",
            "description": "Имя пользователя"
          },
          "breakpoints": {
            "type": "array",
            "description": "Список точек останова",
            "items": {
              "type": "string",
              "example": "Module.bsl:45"
            }
          }
        },
        "required": ["infobase", "user"]
      }
    },
    {
      "name": "evaluate_expression",
      "description": "Вычисляет выражение в контексте отладки",
      "inputSchema": {
        "type": "object",
        "properties": {
          "expression": {
            "type": "string",
            "description": "1С выражение для вычисления"
          }
        },
        "required": ["expression"]
      }
    },
    {
      "name": "get_call_stack",
      "description": "Получает текущий стек вызовов"
    },
    {
      "name": "get_local_variables",
      "description": "Получает значения локальных переменных"
    }
  ]
}