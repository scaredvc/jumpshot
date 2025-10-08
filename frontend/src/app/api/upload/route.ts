import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  try {
    const formData = await request.formData()
    const video = formData.get('video') as File
    
    let djangoFormData = new FormData()
    djangoFormData.append('video', video)

    const djangoResponse = await fetch("http://localhost:8000/api/upload/", {
      method: "POST",
      body: djangoFormData,
    })

    if (!djangoResponse.ok) {
      throw new Error('Failed to upload video')
    }

    const djangoData = await djangoResponse.json()
    return NextResponse.json(djangoData)
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to upload video' },
      { status: 500 }
    )
  }
} 