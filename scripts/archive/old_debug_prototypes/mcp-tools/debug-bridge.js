const com = require('win32ole');

class DebugBridge {
  constructor() {
    this.connection = null;
  }

  async attachTo1C(infobase, user, password = "") {
    try {
      const v83 = new com.Dispatch('V83.COMConnector');
      this.connection = v83.Connect(`File="${infobase}";Usr="${user}";Pwd="${password}";`);
      return { status: "attached", infobase };
    } catch (error) {
      return { status: "error", message: error.message };
    }
  }

  async setBreakpoint(module, line) {
    if (!this.connection) {
      throw new Error("Нет подключения к 1С");
    }
    return this.connection.DebugSetBreakpoint(module, line);
  }

  async evaluateExpression(expr) {
    if (!this.connection) {
      throw new Error("Нет подключения к 1С");
    }
    try {
      const result = this.connection.DebugEvaluate(expr);
      return { success: true, value: result };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  async getCallStack() {
    if (!this.connection) {
      throw new Error("Нет подключения к 1С");
    }
    return this.connection.DebugGetCallStack();
  }

  async getVariables() {
    if (!this.connection) {
      throw new Error("Нет подключения к 1С");
    }
    return this.connection.DebugGetLocalVars();
  }

  disconnect() {
    if (this.connection) {
      this.connection = null;
    }
  }
}

// Глобальный экземпляр
const bridge = new DebugBridge();

// Экспорт MCP инструментов
module.exports = {
  tools: [
    {
      name: "debug_attach",
      handler: async (params) => {
        return await bridge.attachTo1C(
          params.infobase,
          params.user,
          params.password
        );
      }
    },
    {
      name: "debug_eval",
      handler: async (params) => {
        return await bridge.evaluateExpression(params.expression);
      }
    },
    {
      name: "debug_stack",
      handler: async () => {
        return await bridge.getCallStack();
      }
    },
    {
      name: "debug_vars",
      handler: async () => {
        return await bridge.getVariables();
      }
    }
  ]
};