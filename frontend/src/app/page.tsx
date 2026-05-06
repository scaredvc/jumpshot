import ModeToggle from "@/components/ModeToggle";
import VideoUpload from "@/components/VideoUpload";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

export default function Home() {
  return (
    <div className="page-container">
      <section className="top-section">
        <div className="main-page-name">Jumpshot Comparison Prototype</div>
        <ModeToggle />
      </section>

      <section className="middle-section">
        <div className="w-full max-w-2xl mx-auto space-y-8">
          <div className="text-center space-y-2">
            <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">
              Early prototype
            </p>
            <p className="text-sm text-muted-foreground">
              Exploring why LLMs fail at basketball motion analysis from video alone.
            </p>
          </div>
          <div className="flex justify-center">
            <Select>
              <SelectTrigger className="w-[400px]">
                <SelectValue placeholder="Select an NBA player for comparison" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Steph Curry">Stephen Curry</SelectItem>
                <SelectItem value="Klay Thompson">Klay Thompson</SelectItem>
                <SelectItem value="Kevin Durant">Kevin Durant</SelectItem>
              </SelectContent>
            </Select>
          </div>
          
          <VideoUpload />
        </div>
      </section>

      <section className="bottom-section">
        {/* Future content */}
      </section>
    </div>
  );
}
