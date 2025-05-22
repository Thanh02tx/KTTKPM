import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  isLoggedIn: false,
  user: null,
  messages: [],
};
const MAX_MESSAGES = 100;
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    login: (state, action) => {
      state.isLoggedIn = true;
      state.user = action.payload;
    },
    logout: (state) => {
      state.isLoggedIn = false;
      state.user = null;
      state.messages=[];
    },
    addMessage: (state, action) => {
      state.messages.push(action.payload);
      // Nếu quá 100 tin nhắn thì xoá bớt tin cũ nhất
      if (state.messages.length > MAX_MESSAGES) {
        state.messages.shift(); // xoá tin nhắn đầu tiên (cũ nhất)
      }
    },
    clearMessages: (state) => {
      state.messages = [];
    },
    updateMessage: (state, action) => {
      const { index, newData } = action.payload;
      if (state.messages[index]) {
        state.messages[index] = { ...state.messages[index], ...newData };
      }
    },
  },
});

export const { login, logout ,addMessage,clearMessages,updateMessage} = authSlice.actions;
export default authSlice.reducer;
