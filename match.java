import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;
import java.util.*;

public class match{
    public static void main(String[] args) throws FileNotFoundException, UnsupportedEncodingException {
        if(args.length < 3)
            return;

        int rowX = Integer.parseInt(args[0]);
        int rowY = Integer.parseInt(args[1]);
        int column = Integer.parseInt(args[2]);

        String path1 = "data/pcafeature1";
        String path2 = "data/pcafeature2";

        double[][] featureOne = readArray(path1, rowX, column);
        double[][] featureTwo = readArray(path2, rowY, column);

        // start to match
        ArrayList<Integer> result1 = match(featureOne, featureTwo, column);
        ArrayList<Integer> result2 = match(featureTwo, featureOne, column);

        PrintWriter writer = new PrintWriter("data/match", "UTF-8");
        for (int i = 0; i < rowX; i ++){
            if (result2.get(i) == -1)
                continue;

            if (result1.get(result2.get(i)) == i)
                writer.println(i +" "+ result2.get(i));
        }
        writer.close();

    }


    public static ArrayList<Integer> match(double[][] X, double[][] Y, int column){

        ArrayList<Integer>[][] hashStructure = new ArrayList[8][column];

        for(int i = 0; i < 8; i ++){
            for(int j = 0; j < column; j ++)
                hashStructure[i][j] = new ArrayList<Integer>();
        }

        // Hash all points of X into tha hashStructure
        int rowX = X.length;
        int rowY = Y.length;

        for(int i = 0; i < rowX; i ++){
            for(int j = 0; j < column; j ++){
               int hashValue = (int)(X[i][j] * 4);
               if (hashValue == 8)
                   hashValue = 7;

               hashStructure[hashValue][j].add(i);
            }
        }

        // Hash each point of Y one by one
        ArrayList<Integer> result = new ArrayList<Integer>();

        for(int i = 0; i < rowY; i ++){
            HashMap<Integer, Integer> map = new HashMap<Integer, Integer>();

            for (int j = 0; j < column; j ++){
                int value = (int)(Y[i][j] * 4);
                if (value == 8)
                    value = 7;

                // hashStructure[value][j]
                for (int item: hashStructure[value][j]){
                    if(!map.containsKey(item))
                        map.put(item, 1);
                    else{
                        int currentCount = map.get(item);
                        currentCount += 1;
                        map.put(item, currentCount);
                    }
                }

                // [value+1][j]
                if(value != 7){
                    for (int item: hashStructure[value+1][j]){
                        if(!map.containsKey(item))
                            map.put(item, 1);
                        else{
                            int currentCount = map.get(item);
                            currentCount += 1;
                            map.put(item, currentCount);
                        }
                    }
                }

                // [value-1][j]
                if(value !=0){
                    for (int item: hashStructure[value-1][j]){
                        if(!map.containsKey(item))
                            map.put(item, 1);
                        else{
                            int currentCount = map.get(item);
                            currentCount += 1;
                            map.put(item, currentCount);
                        }
                    }
                }

            }

            // Find out the best match for points in Y
            int maxCount = 0;
            Set<Integer> keys = map.keySet();
            Iterator<Integer> it = keys.iterator();

            int potentialMatch = -1;
            while(it.hasNext()){
                int key = it.next();
                int count = map.get(key);

                if(count > maxCount){
                    maxCount = count;
                    potentialMatch = key;
                }
            }

            if(maxCount < 35)
                result.add(-1);
            else
                result.add(potentialMatch);

//            System.out.println("Y[" +i+ "] "+maxCount+" is matched to X[" +result.get(i)+"]");
        }

        return result;

    }


    public static double[][] readArray(String path, int row, int column) throws FileNotFoundException {
        double[][] featureOne = new double[row][column];

        File file1 = new File(path);
        Scanner scanner = new Scanner(file1);

        int i = 0;
        while(scanner.hasNext()){
            String line = scanner.nextLine();
            String[] items = line.split("\t");

            for(int j = 0; j < 36; j ++){
                String item = items[j];
                featureOne[i][j] = Double.parseDouble(item);
            }

            i ++;
        }

        return featureOne;

    }

}
