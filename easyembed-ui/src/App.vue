<template>
  <div style="padding: 20px;">
    <h1>EasyEmbed</h1>

    <!-- File input -->
    <div>
      <label>Select File:</label><br>
      <input type="file" @change="handleFile" />
    </div>

    <br>

    <!-- Extended toggle -->
    <div>
      <label>
        <input type="checkbox" v-model="extended" />
        Enable Extended Codecs
      </label>
    </div>

    <br>

    <!-- Submit -->
    <button @click="submit" :disabled="!file">
      Convert
    </button>

    <p>{{ status }}</p>

    <h2>Processed Files</h2>

    <div v-for="file in files" :key="file" style="margin-bottom: 20px;">
      <p>{{ file }}</p>

      <video
        v-if="file.endsWith('.mp4')"
        controls
        width="400"
        :src="`/media/${file}`"
      ></video>

      <br>

      <button @click="copyLink(file)">
        Copy Link
      </button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      file: null,
      extended: false,
      status: "",
      files: [] // For listing processed files
    }
  },

  mounted() {
    this.loadFiles()
  },

  methods: {
    handleFile(event) {
      this.file = event.target.files[0]
    },

    async submit() {
      if (!this.file) {
        this.status = "Please select a file first."
        return
      }

      const formData = new FormData()
      formData.append("file", this.file)
      formData.append("extended", this.extended)

      this.status = "Uploading..."

      const res = await fetch("/upload", {
        method: "POST",
        body: formData
      })
      
      if (!res.ok) {
        let errorMessage = "Upload failed."

        try {
          const err = await res.json()
          errorMessage = err.detail || errorMessage
        } catch (e) {}
        
        this.status = errorMessage
        return
      }

      const data = await res.json()
      const jobId = data.job_id

      console.log(data)
      this.status = "Processing..."
      this.pollJob(jobId)
    },

    pollJob(jobId) {
      const interval = setInterval(async () => {
        const res = await fetch(`/status/${jobId}`)
        const data = await res.json()

        if (data.status === "processing") {
          this.status = `Processing... ${data.progress}%`
        } 

        if (data.status === "completed") {
          clearInterval(interval)
          this.status = "Completed!"
        }

        if (data.status === "error") {
          clearInterval(interval)
          this.status = `Error: ${data.error}`
        }
      }, 500)
    },
    async loadFiles() {
      const res = await fetch("/files")
      const data = await res.json()
      this.files = data.files
    },
    copyLink(file) {
      const base = window.location.origin
      const url = `${base}/media/${file}`

      navigator.clipboard.writeText(url)
        .then(() => {
          alert("Link copied to clipboard!")
        })
        .catch(err => {
          alert("Failed to copy link.")
        })
        }
  }
}
</script>