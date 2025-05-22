import React, { useState, useEffect, useRef } from 'react';
import { Outlet } from 'react-router-dom';
import { MessageCircle, Minus, MousePointer } from 'lucide-react';
import { useDispatch, useSelector } from 'react-redux';
import { addMessage, updateMessage } from '../../redux/slides/authSlide';
import { predictHeart } from '../../service/erhService';
import Lightbox from 'yet-another-react-lightbox';
import 'yet-another-react-lightbox/styles.css';
import Fullscreen from 'yet-another-react-lightbox/plugins/fullscreen';
import Zoom from 'yet-another-react-lightbox/plugins/zoom';
const MainLayout = () => {
    const messages = useSelector((state) => state.auth.messages);
    const messagesEndRef = useRef(null);
    const dispatch = useDispatch();
    const [isChatOpen, setIsChatOpen] = useState(false);
    const [inputMessage, setInputMessage] = useState('');
    const [hasGreeted, setHasGreeted] = useState(false);
    const [openPreview, setOpenPreview] = useState(false);
    const [currentIndex, setCurrentIndex] = useState(0);
    const [imageBook, setImageBook] = useState([
        'https://res.cloudinary.com/dh7zungyf/image/upload/v1747814177/b-1_g82fdm.jpg',
        'https://res.cloudinary.com/dh7zungyf/image/upload/v1747814177/b-2_oahdtg.jpg',
        'https://res.cloudinary.com/dh7zungyf/image/upload/v1747814176/b-3_ra7jpa.jpg',
        'https://res.cloudinary.com/dh7zungyf/image/upload/v1747814177/b-4_mtlotz.jpg'
    ])
    const formData = {
        age: '',
        sex: '',          // giới tính (1 = nam, 0 = nữ)
        cp: '',           // loại đau ngực (0-3)
        trestbps: '',     // huyết áp nghỉ (mm Hg)
        chol: '',         // cholesterol trong huyết thanh (mg/dl)
        fbs: '',          // đường huyết lúc đói > 120 mg/dl (1 = true, 0 = false)
        restecg: '',      // kết quả điện tâm đồ lúc nghỉ (0-2)
        thalach: '',      // nhịp tim tối đa đạt được
        exang: '',        // có đau thắt ngực khi gắng sức không? (1 = có, 0 = không)
        oldpeak: '',      // ST chênh xuống do gắng sức (so với nghỉ ngơi)
        slope: '',        // độ dốc đoạn ST khi gắng sức (0-2)
        ca: '',           // số lượng mạch chính được nhuộm màu bằng fluoroscopy (0-3)
        thal: '',         // loại thalassemia (1 = bình thường, 2 = cố định khiếm khuyết, 3 = có thể đảo ngược khiếm khuyết)
        isSubmitted: false
    };
    useEffect(() => {
        if (isChatOpen && messages.length === 0) {
            const greeting = { role: 'bot', status: 'greeting' };
            const options = { role: 'bot', status: 'options' };

            dispatch(addMessage(greeting));
            const timer = setTimeout(() => {
                dispatch(addMessage(options));
            }, 800);

            return () => clearTimeout(timer);
        }
    }, [isChatOpen]);
    useEffect(() => {
        if (isChatOpen) {
            messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        }
    }, [isChatOpen]);
    // const handleSendMessage = () => {
    //     if (inputMessage.trim() === '') return;

    //     const userMessage = { role: 'user', content: inputMessage.trim() };
    //     const botReply = { role: 'bot', content: '🤖 Cảm ơn bạn! Tôi đang xử lý yêu cầu...' };

    //     dispatch(addMessage(userMessage));
    //     dispatch(addMessage(botReply));

    //     setInputMessage('');
    // };

    const handleOptionClick = (option, status) => {
        const userMessage = { role: 'user', content: option };
        dispatch(addMessage(userMessage));
        setTimeout(() => {
            if (status === 'predict_heart') {
                dispatch(addMessage({ role: 'bot', status, ...formData }));
            } else {
                dispatch(addMessage({ role: 'bot', status }));
            }
        }, 800);
    };
    const handleSubmit = async (e, index) => {
        e.preventDefault();
        const targetMessage = messages[index];
        if (targetMessage) {
            const fieldOrder = [
                'age', 'sex', 'cp', 'trestbps', 'chol',
                'fbs', 'restecg', 'thalach', 'exang',
                'oldpeak', 'slope', 'ca', 'thal'
            ];
            const formDataArray = fieldOrder.map(key => Number(targetMessage[key]));
            let res = await predictHeart({features:formDataArray})
            if(res?.errCode===0){
                if(res?.data?.label === 0) dispatch(addMessage({role:'bot',content:'Bạn không bị bệnh tim!'}))
                if(res?.data?.label === 1) dispatch(addMessage({role:'bot',content:'Bạn có thể bị bệnh tim!'}))
                dispatch(updateMessage({ index, newData: { 'isSubmitted': true } }));
            }
        }
    };
    const handleChange = (index, e) => {
        const { name, value } = e.target;
        dispatch(updateMessage({ index, newData: { [name]: value } }));
    };
    const renderMessageContent = (msg, index) => {
        if (msg.status === 'greeting') {
            return '👋 Xin chào! Tôi có thể giúp gì cho bạn?';
        }

        if (msg.status === 'options') {
            return (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <button onClick={() => handleOptionClick('🗓 Đặt lịch khám', 'book_appointment')} style={buttonStyle}>🗓 Đặt lịch khám</button>
                    {/* <button onClick={() => handleOptionClick('📋 Xem lịch sử', 'view_history')} style={buttonStyle}>📋 Xem lịch sử</button> */}
                    <button onClick={() => handleOptionClick('❤️ Dự đoán bệnh tim', 'predict_heart')} style={buttonStyle}>❤️ Dự đoán bệnh tim</button>
                    <button onClick={() => handleOptionClick('❓ Hỗ trợ khác', 'other')} style={buttonStyle}>❓ Hỗ trợ khác</button>
                </div>
            );
        }
        if (msg.status === 'other') {
            return 'Vui lòng liên hệ 0916xxxxxx để được trợ giúp!';
        }
        if (msg.status === 'book_appointment') {
            return (
                <div>
                    <p>👉 Vui lòng làm theo các bước sau:</p>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                        {imageBook.map((url, index) => (
                            <img
                                key={index}
                                src={url}
                                alt={`step-${index + 1}`}
                                onClick={() => {
                                    setCurrentIndex(index);     // 👈 Đặt đúng ảnh đang click
                                    setOpenPreview(true);       // 👈 Mở lightbox
                                }}
                                style={{
                                    width: '100%',
                                    height: '100px',
                                    objectFit: 'cover',
                                    borderRadius: '8px',
                                    border: '1px solid #e5e7eb',
                                    cursor: 'pointer',
                                    transition: 'transform 0.2s',
                                }}
                                onMouseOver={(e) => e.currentTarget.style.transform = 'scale(1.02)'}
                                onMouseOut={(e) => e.currentTarget.style.transform = 'scale(1)'}
                            />
                        ))}
                    </div>
                </div>
            );
        }
        if (msg.status === 'predict_heart') {
            return (
                <form
                    onSubmit={(e) => handleSubmit(e, index)}
                    style={{
                        maxHeight: '350px',
                        overflowY: 'auto',
                        display: 'flex',
                        flexDirection: 'column',
                        gap: '8px',
                    }}
                >
                    <input
                        name="age"
                        type="number"
                        min="1"
                        max="120"
                        placeholder="Tuổi"
                        required
                        disabled={msg.isSubmitted}
                        defaultValue={msg.age}
                        onChange={(e) => handleChange(index, e)}
                    />

                    <select
                        name="sex"
                        required
                        disabled={msg.isSubmitted}
                        defaultValue={msg.sex}
                        onChange={(e) => handleChange(index, e)}
                    >
                        <option value="">Giới tính</option>
                        <option value="1">Nam</option>
                        <option value="0">Nữ</option>
                    </select>

                    <select
                        name="cp"
                        required
                        disabled={msg.isSubmitted}
                        defaultValue={msg.cp}
                        onChange={(e) => handleChange(index, e)}
                    >
                        <option value="">Loại đau ngực</option>
                        <option value="0">Đau ngực điển hình</option>
                        <option value="1">Đau ngực không do tim</option>
                        <option value="2">Đau thực quản</option>
                        <option value="3">Không có triệu chứng</option>
                    </select>

                    <input
                        name="trestbps"
                        type="number"
                        min="50"
                        max="250"
                        placeholder="Huyết áp lúc nghỉ (mmHg)"
                        required
                        disabled={msg.isSubmitted}
                        defaultValue={msg.trestbps}
                    />

                    <input
                        name="chol"
                        type="number"
                        min="100"
                        max="600"
                        placeholder="Cholesterol trong máu (mg/dL)"
                        required
                        disabled={msg.isSubmitted}
                        defaultValue={msg.chol}
                        onChange={(e) => handleChange(index, e)}
                    />

                    <select
                        name="fbs"
                        required
                        disabled={msg.isSubmitted}
                        defaultValue={msg.fbs}
                        onChange={(e) => handleChange(index, e)}
                    >
                        <option value="">Đường huyết lúc đói &gt; 120 mg/dl (fbs)</option>
                        <option value="1">Có</option>
                        <option value="0">Không</option>
                    </select>

                    <select
                        name="restecg"
                        required
                        disabled={msg.isSubmitted}
                        defaultValue={msg.restecg}
                        onChange={(e) => handleChange(index, e)}
                    >
                        <option value="">Kết quả điện tâm đồ</option>
                        <option value="0">Bình thường</option>
                        <option value="1">Bất thường sóng ST-T</option>
                        <option value="2">Tăng kích thước thất trái</option>
                    </select>

                    <input
                        name="thalach"
                        type="number"
                        min="50"
                        max="220"
                        placeholder="Nhịp tim tối đa đạt được"
                        required
                        disabled={msg.isSubmitted}
                        defaultValue={msg.thalach}
                        onChange={(e) => handleChange(index, e)}
                    />

                    <select
                        name="exang"
                        required
                        disabled={msg.isSubmitted}
                        defaultValue={msg.exang}
                        onChange={(e) => handleChange(index, e)}
                    >
                        <option value="">Đau thắt ngực khi tập thể dục</option>
                        <option value="1">Có</option>
                        <option value="0">Không</option>
                    </select>

                    <input
                        name="oldpeak"
                        type="number"
                        step="0.1"
                        min="0"
                        max="10"
                        placeholder="Độ giảm ST khi tập thể dục"
                        required
                        disabled={msg.isSubmitted}
                        defaultValue={msg.oldpeak}
                        onChange={(e) => handleChange(index, e)}
                    />

                    <select
                        name="slope"
                        required
                        disabled={msg.isSubmitted}
                        defaultValue={msg.slope}
                        onChange={(e) => handleChange(index, e)}
                    >
                        <option value="">Độ dốc đoạn ST khi tập thể dục</option>
                        <option value="0">Tăng dần</option>
                        <option value="1">Bằng phẳng</option>
                        <option value="2">Giảm dần</option>
                    </select>

                    <select
                        name="ca"
                        required
                        disabled={msg.isSubmitted}
                        defaultValue={msg.ca}
                        onChange={(e) => handleChange(index, e)}
                    >
                        <option value="">Số lượng mạch chính được nhuộm màu</option>
                        <option value="0">0</option>
                        <option value="1">1</option>
                        <option value="2">2</option>
                        <option value="3">3</option>
                    </select>

                    <select
                        name="thal"
                        required
                        disabled={msg.isSubmitted}
                        defaultValue={msg.thal}
                        onChange={(e) => handleChange(index, e)}
                    >
                        <option value="">Kết quả chụp thallium (stress thalium)</option>
                        <option value="1">Bình thường</option>
                        <option value="2">Khuyết điểm cố định</option>
                        <option value="3">Khuyết điểm hồi phục</option>
                    </select>

                    <button
                        type="submit"
                        style={{
                            backgroundColor: '#2563eb',
                            color: 'white',
                            padding: '10px',
                            borderRadius: '8px',
                            // cursor: 'pointer',
                        }}
                        disabled={msg.isSubmitted}
                    >
                        Gửi dự đoán
                    </button>
                </form>

            );
        }

        return msg.content;
    };

    const buttonStyle = {
        backgroundColor: '#e0f2fe',
        border: '1px solid #93c5fd',
        borderRadius: '8px',
        padding: '8px 12px',
        cursor: 'pointer',
        fontSize: '14px',
        textAlign: 'left',
    };
    const handleShowMenu=()=>{
        const greeting = { role: 'bot', status: 'greeting' };
            const options = { role: 'bot', status: 'options' };

            dispatch(addMessage(greeting));
            const timer = setTimeout(() => {
                dispatch(addMessage(options));
            }, 800);

            return () => clearTimeout(timer);
    }
    return (
        <div style={{ position: 'relative', minHeight: '100vh', backgroundColor: '#f9fafb' }}>
            <Outlet />

            <div style={{ position: 'fixed', bottom: '60px', right: '40px', zIndex: 9999 }}>
                {isChatOpen ? (
                    <div
                        style={{
                            width: '400px',
                            height: '500px',
                            backgroundColor: '#ffffff',
                            boxShadow: '0 10px 30px rgba(0,0,0,0.1)',
                            borderRadius: '1rem',
                            overflow: 'hidden',
                            display: 'flex',
                            flexDirection: 'column',
                            border: '1px solid #e5e7eb',
                        }}
                    >
                        {/* Header */}
                        <div
                            style={{
                                padding: '12px 16px',
                                backgroundColor: '#2563eb',
                                color: 'white',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                            }}
                        >
                            <span>💬 Trợ lý ảo</span>
                            <button
                                onClick={() => setIsChatOpen(false)}
                                style={{
                                    background: 'none',
                                    border: 'none',
                                    color: 'white',
                                    cursor: 'pointer',
                                }}
                            >
                                <Minus size={20} />
                            </button>
                        </div>

                        {/* Chat Content */}
                        <div
                            style={{
                                flex: 1,
                                padding: '16px',
                                overflowY: 'auto',
                                display: 'flex',
                                flexDirection: 'column',
                                gap: '8px',
                            }}
                        >
                            {messages.map((msg, index) => (
                                <div
                                    key={index}
                                    style={{
                                        maxWidth: '80%',
                                        alignSelf: msg.role === 'bot' ? 'flex-start' : 'flex-end',
                                        backgroundColor: msg.role === 'bot' ? '#f3f4f6' : '#dbeafe',
                                        padding: '10px 14px',
                                        borderRadius: '12px',
                                        wordBreak: 'break-word',
                                        fontSize: '14px',
                                        color: '#374151',
                                    }}
                                >
                                    {renderMessageContent(msg, index)}
                                </div>
                            ))}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Input Message */}
                        {/* <div
                            style={{
                                display: 'flex',
                                borderTop: '1px solid #e5e7eb',
                                padding: '10px',
                            }}
                        >
                            <input
                                type="text"
                                value={inputMessage}
                                onChange={(e) => setInputMessage(e.target.value)}
                                onKeyDown={(e) => {
                                    if (e.key === 'Enter') handleSendMessage();
                                }}
                                placeholder="Nhập tin nhắn..."
                                style={{
                                    flex: 1,
                                    padding: '8px 12px',
                                    borderRadius: '8px',
                                    border: '1px solid #d1d5db',
                                    marginRight: '8px',
                                }}
                            />
                            <button
                                onClick={handleSendMessage}
                                style={{
                                    backgroundColor: '#2563eb',
                                    color: 'white',
                                    border: 'none',
                                    padding: '8px 16px',
                                    borderRadius: '8px',
                                    cursor: 'pointer',
                                }}
                            >
                                Menu
                            </button>
                        </div> */}
                        <div
                            style={{
                                display: 'flex',
                                borderTop: '1px solid #e5e7eb',
                                padding: '10px',
                            }}
                        >
                            {/* <div
                                style={{
                                    flex: 1,
                                    padding: '8px 12px',
                                    // borderRadius: '8px',
                                    // border: '1px solid #d1d5db',
                                    marginRight: '8px',
                                }}
                            ></div> */}
                            <button
                                onClick={handleShowMenu}
                                style={{
                                    backgroundColor: '#2563eb',
                                    color: 'white',
                                    border: 'none',
                                    padding: '8px 16px',
                                    borderRadius: '8px',
                                    cursor: 'pointer',
                                    marginLeft: 'auto'
                    
                                }}
                            >
                                Menu
                            </button>
                        </div>
                    </div>
                ) : (
                    <button
                        style={{
                            backgroundColor: '#2563eb',
                            color: '#ffffff',
                            padding: '12px',
                            borderRadius: '9999px',
                            boxShadow: '0 8px 16px rgba(0,0,0,0.2)',
                            border: 'none',
                            cursor: 'pointer',
                            transition: 'background-color 0.2s',
                        }}
                        onClick={() => setIsChatOpen(true)}
                        title="Trợ lý ảo"
                        onMouseOver={(e) => (e.currentTarget.style.backgroundColor = '#1d4ed8')}
                        onMouseOut={(e) => (e.currentTarget.style.backgroundColor = '#2563eb')}
                    >
                        <MessageCircle size={50} />
                    </button>
                )}
            </div>
            <Lightbox
                open={openPreview}
                close={() => setOpenPreview(false)}
                slides={imageBook.map((src) => ({ src }))}
                index={currentIndex}          // 👈 Quan trọng: truyền đúng index
                plugins={[Fullscreen, Zoom]}
                carousel={{ zoom: true }}
            />

        </div>
    );
};

export default MainLayout;
