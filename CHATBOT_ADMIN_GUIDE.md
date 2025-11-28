# 🤖 AI Chatbot & Admin Guide

## ✅ Fixed Issues

### Mobile Responsiveness
- ✅ **No more zooming** - Viewport locked with `user-scalable=no`
- ✅ **44px touch targets** - All buttons meet Apple Human Interface Guidelines
- ✅ **16px font size** - Prevents iOS auto-zoom on input focus
- ✅ **Full-screen chatbot** - Mobile uses 100vh, desktop uses 420px window
- ✅ **Safe area support** - Works with iPhone notches and home indicators

### Chatbot Backend
- ✅ **Auto-loads on startup** - Knowledge base loads from Firebase when app starts
- ✅ **Auto-trains on upload** - Every document upload automatically retrains chatbot
- ✅ **Manual train button** - Admin can manually refresh knowledge base anytime
- ✅ **Firebase persistence** - All documents stored in Firebase Realtime Database

## 📱 How to Use Admin Panel

### Access Admin Panel
1. Login as admin user
2. Navigate to: `https://your-app.azurewebsites.net/admin`
3. Click "AI Chatbot" tab

### Upload Documents (3 Methods)

#### Method 1: Upload File
1. Click **"Upload Document"** button
2. Select **"File"** tab
3. Click the upload area
4. Choose file: `.txt`, `.pdf`, `.md`, `.doc`, `.docx`
5. ✨ **Auto-trains immediately** after upload!
6. See success message with total document count

#### Method 2: Add from URL
1. Click **"Upload Document"** button
2. Select **"URL"** tab
3. Enter article/webpage URL
4. Click **"Upload URL"**
5. ✨ **Auto-trains immediately** after fetching content!

#### Method 3: Paste Text
1. Click **"Upload Document"** button
2. Select **"Text"** tab
3. Enter document title
4. Paste your content (FAQs, guidelines, etc.)
5. Click **"Upload Text"**
6. ✨ **Auto-trains immediately** after saving!

### Manual Training
- Click **"Train Chatbot"** button anytime
- Reloads all documents from Firebase
- Shows total document count
- Use if you suspect chatbot data is stale

### Delete Documents
1. Find document in list
2. Click 🗑️ trash icon
3. Confirm deletion
4. ✨ **Auto-retrains** after deletion!

## 🎯 Chatbot Features

### For Users
- **AI Health Assistant** - Answers diabetes and health questions
- **Context-Aware** - Knows your prediction history
- **RAG Technology** - Uses uploaded documents for accurate answers
- **Chat History** - Saves conversation across sessions
- **Mobile & Desktop** - Responsive design for all devices

### For Admins
- **Upload medical articles** - PDFs, documents, web pages
- **Custom knowledge** - Add FAQs, guidelines, policies
- **Real-time updates** - Changes reflect immediately
- **Document management** - View, delete, organize content
- **Training control** - Auto or manual retraining

## 🔧 Technical Details

### Backend Files
- `flask_app.py` - Main chatbot logic and admin endpoints
- `firebase_config.py` - Firebase database connection
- Lines 3492-3956 - Chatbot routes and knowledge base loader

### Frontend Files
- `frontend/src/components/HealthChatbot.tsx` - Chatbot UI component
- `frontend/src/pages/AdminPage.tsx` - Admin panel with upload modal
- Mobile-first responsive design

### API Endpoints
```
POST /api/chatbot              - Send message to chatbot
GET  /api/chatbot/history      - Get chat history
POST /api/chatbot/clear        - Clear chat history

GET    /api/admin/chatbot/documents       - List all documents
POST   /api/admin/chatbot/upload          - Upload file/URL/text
POST   /api/admin/chatbot/train           - Manual training
DELETE /api/admin/chatbot/documents/:id   - Delete document
```

### Knowledge Base Flow
```
1. Admin uploads document
   ↓
2. Saved to Firebase (/chatbot_documents/:id)
   ↓
3. load_chatbot_knowledge_base() called
   ↓
4. All documents loaded into memory
   ↓
5. Chatbot uses documents to answer questions
```

## 📊 Monitoring

### Check if Chatbot is Working
1. Open chatbot widget (bottom-right)
2. Ask: "What is diabetes?"
3. Should get detailed medical answer
4. If error, check Azure logs for GROQ_API_KEY

### Check Document Count
1. Go to Admin Panel → AI Chatbot tab
2. See document count in header
3. Should match number of uploaded files

### Firebase Data Structure
```json
{
  "chatbot_documents": {
    "doc_20251128_120000": {
      "filename": "diabetes_guide.pdf",
      "type": "file",
      "content": "...",
      "uploaded_at": "2025-11-28T12:00:00",
      "uploaded_by": "admin_user_id",
      "size": 15234
    }
  }
}
```

## 🐛 Troubleshooting

### Chatbot Not Responding
- ✅ Check GROQ_API_KEY is set in Azure Portal
- ✅ Check Firebase credentials are valid
- ✅ Click "Train Chatbot" to reload knowledge base
- ✅ Check browser console for errors

### Upload Fails
- ✅ Check file type (.txt, .pdf, .md, .doc, .docx only)
- ✅ Check file size (under 10MB recommended)
- ✅ Check Firebase database is accessible
- ✅ Verify admin role in session

### Mobile View Issues
- ✅ Clear browser cache and reload
- ✅ Check viewport meta tag in index.html
- ✅ Test on actual device (not just browser DevTools)

### Training Doesn't Work
- ✅ Check Flask logs: `az webapp log tail --name diabetes-predictor-ai --resource-group diabetes-predictor-rg`
- ✅ Verify Firebase initialized successfully
- ✅ Check `load_chatbot_knowledge_base()` logs on startup

## 🚀 Deployment Notes

### What Gets Deployed
- ✅ Flask backend with chatbot routes
- ✅ React frontend with admin panel
- ✅ Docker container (~12 min build)
- ✅ Auto-deployed to Azure

### After Deployment
1. Wait ~15 minutes for full deployment
2. Check main page loads: `https://your-app.azurewebsites.net`
3. Test chatbot widget (bottom-right button)
4. Login as admin and test upload
5. Verify documents persist after refresh

## 📖 Best Practices

### Content Quality
- ✅ Upload authoritative medical sources
- ✅ Use clear, accurate language
- ✅ Keep documents focused on diabetes/health
- ✅ Update content regularly

### Document Organization
- ✅ Use descriptive filenames
- ✅ Group related content
- ✅ Remove outdated information
- ✅ Keep knowledge base under 50 documents

### Performance
- ✅ Limit document size (under 10KB extracted text)
- ✅ Train chatbot during low-traffic times
- ✅ Monitor response times
- ✅ Clean up unused documents

## 🎉 Success Indicators

Your chatbot is working correctly when:
- ✅ Chatbot widget appears on all pages
- ✅ Admin can upload documents successfully
- ✅ Training completes without errors
- ✅ Chatbot provides detailed health answers
- ✅ Mobile view is responsive and non-zooming
- ✅ Documents persist across deployments
- ✅ Chat history is maintained

## 📞 Support

If you encounter issues:
1. Check Azure logs: `az webapp log tail --name diabetes-predictor-ai --resource-group diabetes-predictor-rg`
2. Check browser console for JavaScript errors
3. Verify Firebase console shows documents under `/chatbot_documents`
4. Test with simple text upload first before complex PDFs
5. Restart Azure app: `az webapp restart --name diabetes-predictor-ai --resource-group diabetes-predictor-rg`

---

**Last Updated:** November 28, 2025
**Version:** 2.0.0 - Auto-training release
