import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;
import java.util.*;
import java.lang.Math;

public class match{
    public static void main(String[] args) throws FileNotFoundException, UnsupportedEncodingException {
        if(args.length < 3)
            return;

        int rowX = Integer.parseInt(args[0]);
        int rowY = Integer.parseInt(args[1]);
        int column = Integer.parseInt(args[2]);

        String path1 = "pcafeature1";
        String path2 = "pcafeature2";

        double[][] featureOne = readArray(path1, rowX, column);
        double[][] featureTwo = readArray(path2, rowY, column);

        // start to match
        ArrayList<ArrayList<Integer>> result1 = match(featureOne, featureTwo, column);
        ArrayList<ArrayList<Integer>> result2 = match(featureTwo, featureOne, column);

        PrintWriter writer = new PrintWriter("data/match", "UTF-8");
        for (int i = 0; i < rowX; i ++){
            if (result2.get(i).size() == 0)
                continue;

            // potential stores potential indices
            ArrayList<Integer> potential = new ArrayList<Integer>();
            ArrayList<Integer> test = result2.get(i);

            for(int twoIndice: test){
                if (result1.get(twoIndice).contains(i))
                    potential.add(twoIndice);
            }

            if(potential.size() == 0)
                continue;
            else if (potential.size() == 1)
                writer.println(i +" "+ potential.get(0));
            else{
                // Select the nearest neighbor
                int potentialSize = potential.size();
                double[] distances = new double[potentialSize];

                for (int m = 0; m < potentialSize; m ++){
                    int n = potential.get(m);
                    double distance = 0.0;

                    for (int index = 0; index < column; index ++)
                        distance += Math.pow((featureOne[i][index] - featureTwo[n][index]), 2);

                    distances[m] = distance;
                }

                double minDistance = distances[0];
                int minIndice = 0;

                for (int m1 = 1; m1 < potentialSize; m1 ++){
                    if (minDistance > distances[m1]){
                        minDistance = distances[m1];
                        minIndice = m1;
                    }

                }

                writer.println(i +" "+ potential.get(minIndice));

            }

        }
        writer.close();
    }


    public static ArrayList<ArrayList<Integer>> match(double[][] X, double[][] Y, int column){

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
        ArrayList<ArrayList<Integer>> result = new ArrayList<ArrayList<Integer>>();


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

            ArrayList<Integer> potential = new ArrayList<Integer>();
            Set<Integer> keys = map.keySet();
            Iterator<Integer> it = keys.iterator();

            while(it.hasNext()){
                int key = it.next();
                int count = map.get(key);

                if (count == 36){
                    potential.add(key);
                }
            }

            result.add(potential);
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
