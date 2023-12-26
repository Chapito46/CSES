package seleniumapp;
import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.devtools.DevTools;
import org.openqa.selenium.devtools.v120.network.Network;
import org.openqa.selenium.devtools.v120.network.model.Headers;
import org.openqa.selenium.interactions.Actions;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.time.Duration;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import java.io.FileWriter;
import java.io.IOException;  // Import the IOException class to handle errors
import java.util.logging.Level;
import java.util.logging.Logger;

public class MozaikGet {
    public static void main(String[] args) {
        Logger logger = Logger.getLogger("");
        logger.setLevel(Level.SEVERE);
        ChromeDriver driver = new ChromeDriver();
        driver.get("https://mozaikportail.ca/");
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(1000));
        wait.until(ExpectedConditions.presenceOfElementLocated(By.xpath("//button[@class=\"btnConnexion btn\"]")));
        driver.findElement(By.xpath("//button[@class=\"btnConnexion btn\"]")).click();
        try{
            TimeUnit.SECONDS.sleep(10);
            wait.until(ExpectedConditions.urlToBe("https://mozaikportail.ca/"));
            DevTools devTools = driver.getDevTools();
            devTools.createSession();
            devTools.send(Network.enable(Optional.empty(),Optional.empty(),Optional.empty()));
            devTools.addListener(Network.requestWillBeSent(),
                    request -> {

                        if (request.getRequest().getUrl().contains("activitescalendrier")) {
                            String url = request.getRequest().getUrl();
                            try {
                                FileWriter activite_calendrier_url = new FileWriter("activite_calendrier_url.txt");
                                activite_calendrier_url.write(url);
                                activite_calendrier_url.close();
//                                System.out.println("Successfully wrote to activite_calendrier_url file.");
                            } catch (IOException e) {
                                System.out.println("An error occurred.");
                                e.printStackTrace();
                            }
                        }
                        if(request.getRequest().getUrl().contains("https://apiaffairesmp.mozaikportail.ca/api/organisationScolaire/calendrierScolaire/")){
                            String url = request.getRequest().getUrl();
                            try {
                                FileWriter calendrier_scolaire_url = new FileWriter("calendrier_scolaire_url.txt");
                                calendrier_scolaire_url.write(url);
                                calendrier_scolaire_url.close();
//                                System.out.println("Successfully wrote to calendrier_scolaire_url file.");
                            } catch (IOException e) {
                                System.out.println("An error occurred.");
                                e.printStackTrace();
                            }
                            Headers header = request.getRequest().getHeaders();
                            String strheader = header.toString();
                            if (strheader.contains("Bearer")) {
                                String[] arrOfStr = strheader.split(",", 0);

                                for (String a : arrOfStr){
                                    if(a.contains("Bearer")){
                                        String bearertoken = a.replace("Authorization=Bearer ", "").strip();
                                        try {
                                            FileWriter authToken = new FileWriter("authToken.txt");
                                            authToken.write(bearertoken);
                                            authToken.close();
//                                            System.out.println("Successfully wrote to the file.");

//                                            String[] cmd = new String["cmd.exe", "/C", "dir *.*"]
//                                            Runtime rt = Runtime.getRuntime();
//                                            System.out.println("Execing " + cmd[0] + " " + cmd[1]
//                                                    + " " + cmd[2]);
//                                            Runtime rt = Runtime.getRuntime();
//                                            try{
//                                                rt.exec("GoogleCalendar.exe");
//                                            }catch (Exception e){
//                                                System.out.println(e);
//                                            }
                                            driver.close();
                                            ProcessBuilder builder = new ProcessBuilder(
                                                    "cmd.exe", "/c", "start GoogleCalendar.exe");
                                            builder.redirectErrorStream(true);
                                            Process p = builder.start();
                                            BufferedReader r = new BufferedReader(new InputStreamReader(p.getInputStream()));
                                            String line;
                                            while (true) {
                                                line = r.readLine();
                                                if (line == null) { break; }
                                                System.out.println(line);
                                            }
                                            System.exit(0);
//                                            ProcessBuilder pb = new ProcessBuilder("cmd.exe", "/K", "GoogleCalendar.exe");
//                                            pb.start();
//                                            String output = IOUtils.toString(pb.start().getInputStream(), StandardCharsets.UTF_8);
//                                            System.out.println(output);

                                        } catch (IOException e) {
                                            System.out.println("An error occurred.");
                                            e.printStackTrace();
                                        }
                                    }}
                            }

                        }
                    }
                    );

            wait.until(ExpectedConditions.presenceOfElementLocated(By.cssSelector("a[href='#'][onclick=\"event.preventDefault(); changerEspaceTravail('eleve');\"], a[href='#'][onclick=\"event.preventDefault(); changerEspaceTravail('enseignant');\"]")));
            driver.findElement(By.cssSelector("a[href='#'][onclick=\"event.preventDefault(); changerEspaceTravail('eleve');\"], a[href='#'][onclick=\"event.preventDefault(); changerEspaceTravail('enseignant');\"]")).click();
            TimeUnit.SECONDS.sleep(2);
            wait.until(ExpectedConditions.presenceOfElementLocated(By.className("monHoraire__navigation")));
            WebElement element = driver.findElement(By.className("monHoraire__navigation"));
            Actions actions = new Actions(driver);
            actions.moveToElement(element).click().perform();

            wait.until(ExpectedConditions.elementToBeClickable(By.className("precedentSuivant__suivant--plein")));
            driver.findElement(By.className("precedentSuivant__suivant--plein")).click();

        }
        catch (InterruptedException e){
            System.out.println("Failed to wait");
        }

    }
}
