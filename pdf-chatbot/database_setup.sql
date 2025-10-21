-- PDFs tabel
CREATE TABLE pdfs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  filename TEXT NOT NULL,
  content TEXT NOT NULL,
  file_size INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Chats tabel
CREATE TABLE chats (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id),
  pdf_id UUID REFERENCES pdfs(id),
  message TEXT NOT NULL,
  response TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- RLS inschakelen
ALTER TABLE pdfs ENABLE ROW LEVEL SECURITY;
ALTER TABLE chats ENABLE ROW LEVEL SECURITY;

-- Policies voor PDFs
CREATE POLICY "Users can view own pdfs" ON pdfs
FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own pdfs" ON pdfs
FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own pdfs" ON pdfs
FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own pdfs" ON pdfs
FOR DELETE USING (auth.uid() = user_id);

-- Policies voor Chats
CREATE POLICY "Users can view own chats" ON chats
FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own chats" ON chats
FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own chats" ON chats
FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own chats" ON chats
FOR DELETE USING (auth.uid() = user_id);